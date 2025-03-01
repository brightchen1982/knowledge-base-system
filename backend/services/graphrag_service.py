import os
import logging
import yaml
from typing import Dict, List, Optional, Any
import networkx as nx
import numpy as np
from .vector_store import VectorStore
from .llm_service import LLMService

logger = logging.getLogger(__name__)

class GraphRAGService:
    def __init__(self, vector_store: VectorStore, llm_service: LLMService,
                config_path: str = "configs/worker.yaml"):
        # 加载配置
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # 存储服务引用
        self.vector_store = vector_store
        self.llm_service = llm_service
        
        # 加载GraphRAG设置
        self.rag_settings = self.config["graphrag"]
        self.similarity_threshold = self.rag_settings["similarity_threshold"]
        self.max_neighbors = self.rag_settings["max_neighbors"]
        self.max_hops = self.rag_settings["max_hops"]
        
        # 初始化图结构
        self.graph = nx.Graph()
        
        logger.info("GraphRAG服务初始化完成")
    
    def update_graph(self, document_id: str = None):
        """
        更新知识图谱，可以指定文档ID更新特定文档，或不指定更新全部
        
        Args:
            document_id (str, optional): 特定文档ID，为None时更新所有文档
        """
        try:
            # 查询条件
            filter_dict = {}
            if document_id:
                filter_dict = {"document_id": document_id}
            
            # 获取所有块
            all_chunks = self.vector_store.query(
                query_vector=[0.0] * 768,  # 使用空向量，将获取所有文档而不是相似匹配
                limit=10000,  # 大量限制，实际上取决于数据库能返回的最大记录数
                filter_=filter_dict
            )
            
            # 清理图形（如果更新特定文档）
            if document_id:
                # 删除与特定文档相关的节点
                nodes_to_remove = [node for node in self.graph.nodes if self.graph.nodes[node].get("document_id") == document_id]
                self.graph.remove_nodes_from(nodes_to_remove)
            else:
                # 重建整个图
                self.graph.clear()
            
            # 为每个块创建节点
            for chunk in all_chunks:
                chunk_id = chunk["id"]
                doc_id = chunk["payload"]["document_id"]
                
                # 添加节点
                self.graph.add_node(
                    chunk_id,
                    document_id=doc_id,
                    text=chunk["payload"]["text"],
                    embedding=chunk["payload"].get("embedding", [])
                )
            
            # 计算相似度并创建边
            chunk_ids = list(self.graph.nodes)
            for i, chunk_id in enumerate(chunk_ids):
                # 获取当前块的向量嵌入
                if not self.graph.nodes[chunk_id].get("embedding"):
                    # 如果没有嵌入，获取文本并生成嵌入
                    text = self.graph.nodes[chunk_id]["text"]
                    embedding = self.llm_service.get_embedding(text)
                    self.graph.nodes[chunk_id]["embedding"] = embedding
                
                current_embedding = self.graph.nodes[chunk_id]["embedding"]
                current_doc_id = self.graph.nodes[chunk_id]["document_id"]
                
                # 为效率考虑，只与同一文档内的块或特殊关系块计算相似度
                for j, other_id in enumerate(chunk_ids):
                    if i == j:
                        continue
                    
                    other_doc_id = self.graph.nodes[other_id]["document_id"]
                    
                    # 同一文档内相邻块自动连接
                    if current_doc_id == other_doc_id and abs(i - j) == 1:
                        self.graph.add_edge(chunk_id, other_id, weight=0.9)
                        continue
                    
                    # 计算其他相似块
                    if not self.graph.nodes[other_id].get("embedding"):
                        # 如果没有嵌入，获取文本并生成嵌入
                        text = self.graph.nodes[other_id]["text"]
                        embedding = self.llm_service.get_embedding(text)
                        self.graph.nodes[other_id]["embedding"] = embedding
                    
                    other_embedding = self.graph.nodes[other_id]["embedding"]
                    
                    # 计算余弦相似度
                    similarity = self._cosine_similarity(current_embedding, other_embedding)
                    
                    # 如果相似度高于阈值，添加边
                    if similarity > self.similarity_threshold:
                        self.graph.add_edge(chunk_id, other_id, weight=similarity)
            
            logger.info(f"知识图谱更新完成，节点数: {self.graph.number_of_nodes()}, 边数: {self.graph.number_of_edges()}")
            
        except Exception as e:
            logger.error(f"更新知识图谱时出错: {str(e)}")
            raise Exception(f"知识图谱更新失败: {str(e)}")
    
    def get_context_for_query(self, query: str, user_id: Optional[str] = None, 
                             document_ids: Optional[List[str]] = None, 
                             max_results: int = 5) -> List[Dict[str, Any]]:
        """
        为查询获取上下文信息
        
        Args:
            query: 用户查询
            user_id: 可选用户ID过滤
            document_ids: 可选文档ID列表过滤
            max_results: 最大返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 相关上下文信息列表
        """
        try:
            # 生成查询嵌入
            query_embedding = self.llm_service.get_embedding(query)
            
            # 准备过滤器
            filter_dict = {}
            if user_id:
                filter_dict["user_id"] = user_id
            if document_ids:
                filter_dict["document_id"] = document_ids
            
            # 首先进行向量搜索找到最相关的入口点
            initial_results = self.vector_store.query(
                query_vector=query_embedding,
                limit=3,  # 获取少量高质量入口点
                filter_=filter_dict
            )
            
            # 扩展结果集
            expanded_results = set()
            for result in initial_results:
                chunk_id = result["id"]
                expanded_results.add(chunk_id)
                
                # 图遍历扩展
                if chunk_id in self.graph:
                    # 获取邻居节点
                    neighbors = self._get_relevant_neighbors(chunk_id, query_embedding, hops=self.max_hops)
                    expanded_results.update(neighbors)
            
            # 将扩展结果转换回详细信息
            detailed_results = []
            for chunk_id in expanded_results:
                # 从图中获取节点信息
                if chunk_id in self.graph:
                    node_data = self.graph.nodes[chunk_id]
                    if "text" in node_data:
                        # 计算与查询的相似度
                        similarity = self._cosine_similarity(
                            query_embedding, 
                            node_data.get("embedding", self.llm_service.get_embedding(node_data["text"]))
                        )
                        
                        detailed_results.append({
                            "id": chunk_id,
                            "text": node_data["text"],
                            "score": similarity,
                            "metadata": {
                                "document_id": node_data.get("document_id", ""),
                            }
                        })
            
            # 排序并限制结果数量
            detailed_results.sort(key=lambda x: x["score"], reverse=True)
            return detailed_results[:max_results]
            
        except Exception as e:
            logger.error(f"获取查询上下文时出错: {str(e)}")
            # 回退到简单向量搜索
            try:
                fallback_results = self.vector_store.query(
                    query_vector=query_embedding,
                    limit=max_results,
                    filter_=filter_dict
                )
                
                # 格式化结果
                return [{
                    "id": result["id"],
                    "text": result["payload"]["text"],
                    "score": result["score"],
                    "metadata": {
                        "document_id": result["payload"].get("document_id", ""),
                    }
                } for result in fallback_results]
            except:
                logger.error("回退搜索也失败")
                return []
    
    def _get_relevant_neighbors(self, start_node: str, query_embedding: List[float], 
                               hops: int = 2) -> List[str]:
        """获取与查询相关的邻居节点"""
        # BFS搜索相关节点
        visited = set([start_node])
        queue = [(start_node, 0)]  # (node, hop)
        relevant_nodes = []
        
        while queue:
            node, hop_count = queue.pop(0)
            
            # 如果超过最大跳数，停止
            if hop_count >= hops:
                continue
            
            # 获取邻居节点
            if node not in self.graph:
                continue
                
            neighbors = list(self.graph.neighbors(node))
            
            # 计算邻居节点与查询的相似度
            neighbor_similarities = []
            for neighbor in neighbors:
                if neighbor in visited:
                    continue
                
                # 获取向量嵌入
                if "embedding" not in self.graph.nodes[neighbor]:
                    text = self.graph.nodes[neighbor]["text"]
                    self.graph.nodes[neighbor]["embedding"] = self.llm_service.get_embedding(text)
                
                embedding = self.graph.nodes[neighbor]["embedding"]
                
                # 计算相似度
                similarity = self._cosine_similarity(query_embedding, embedding)
                neighbor_similarities.append((neighbor, similarity))
            
            # 按相似度排序
            neighbor_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # 取前N个相关邻居
            for neighbor, similarity in neighbor_similarities[:self.max_neighbors]:
                if similarity > self.similarity_threshold and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, hop_count + 1))
                    relevant_nodes.append(neighbor)
        
        return relevant_nodes
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return np.dot(vec1, vec2) / (norm1 * norm2) 
