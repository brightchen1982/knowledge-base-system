import os
import logging
import yaml
from typing import Dict, List, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
import numpy as np

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, config_path: str = "configs/qdrant.yaml"):
        # 加载配置
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # 初始化Qdrant客户端
        self.client = QdrantClient(
            host=self.config["qdrant"]["host"],
            port=self.config["qdrant"]["port"],
            prefer_grpc=self.config["qdrant"]["prefer_grpc"],
            timeout=self.config["qdrant"]["timeout"]
        )
        
        # 获取集合配置
        self.default_collection = self.config["collections"]["default"]["name"]
        self.metadata_collection = self.config["collections"]["metadata"]["name"]
        
        # 初始化集合（如果不存在）
        self._initialize_collections()
        
        logger.info(f"向量存储初始化完成: {self.default_collection}, {self.metadata_collection}")
    
    def _initialize_collections(self):
        """初始化向量集合"""
        collections = [collection.name for collection in self.client.get_collections().collections]
        
        # 初始化文档集合
        if self.default_collection not in collections:
            doc_config = self.config["collections"]["default"]
            self.client.create_collection(
                collection_name=self.default_collection,
                vectors_config=rest.VectorsConfig(
                    size=doc_config["vector_size"],
                    distance=rest.Distance[doc_config["distance"]]
                ),
                optimizers_config=rest.OptimizersConfigDiff(
                    deleted_threshold=doc_config["optimizers"]["deleted_threshold"],
                    vacuum_min_vector_number=doc_config["optimizers"]["vacuum_min_vector_number"]
                ),
                hnsw_config=rest.HnswConfigDiff(
                    m=doc_config["index"]["m"],
                    ef_construct=doc_config["index"]["ef_construct"]
                )
            )
            logger.info(f"创建集合 {self.default_collection}")
        
        # 初始化元数据集合
        if self.metadata_collection not in collections:
            meta_config = self.config["collections"]["metadata"]
            self.client.create_collection(
                collection_name=self.metadata_collection,
                vectors_config=rest.VectorsConfig(
                    size=meta_config["vector_size"],
                    distance=rest.Distance[meta_config["distance"]]
                )
            )
            logger.info(f"创建集合 {self.metadata_collection}")
    
    def add_documents(self, vectors: List[List[float]], payloads: List[Dict[str, Any]], 
                     ids: Optional[List[str]] = None, collection_name: Optional[str] = None) -> List[str]:
        """添加文档向量和元数据"""
        collection_name = collection_name or self.default_collection
        
        # 如果没有提供ID，则生成
        if ids is None:
            ids = [str(i) for i in range(len(vectors))]
        
        # 转换为numpy数组进行验证
        vectors_np = np.array(vectors, dtype=np.float32)
        
        try:
            # 创建点批次
            points = [
                rest.PointStruct(
                    id=str(id_),
                    vector=vector.tolist(),
                    payload=payload
                )
                for id_, vector, payload in zip(ids, vectors_np, payloads)
            ]
            
            # 插入批次
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"向{collection_name}添加了{len(points)}个向量")
            return ids
            
        except Exception as e:
            logger.error(f"向{collection_name}添加向量失败: {str(e)}")
            raise Exception(f"添加向量失败: {str(e)}")
    
    def query(self, query_vector: List[float], limit: int = 5, 
             filter_: Optional[Dict[str, Any]] = None, collection_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索相似向量"""
        collection_name = collection_name or self.default_collection
        
        try:
            # 转换查询向量为numpy数组
            query_vector_np = np.array(query_vector, dtype=np.float32)
            
            # 创建过滤器
            search_filter = None
            if filter_:
                search_filter = rest.Filter(**filter_)
            
            # 执行搜索
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector_np.tolist(),
                limit=limit,
                query_filter=search_filter,
                with_payload=True,
                with_vectors=False
            )
            
            # 格式化结果
            formatted_results = [
                {
                    "id": str(result.id),
                    "score": float(result.score),
                    "payload": result.payload
                }
                for result in results
            ]
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"查询{collection_name}失败: {str(e)}")
            raise Exception(f"查询向量失败: {str(e)}") 
