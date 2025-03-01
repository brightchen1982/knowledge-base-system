import os
import logging
import yaml
from typing import Dict, List, Optional, Any, BinaryIO, Tuple
import uuid
import hashlib
import mimetypes
from datetime import datetime
import redis
import json
from .vector_store import VectorStore
from ..processors.base import get_document_processor
from ..embeddings.model import get_embeddings

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, vector_store: VectorStore, config_path: str = "configs/worker.yaml",
                redis_config_path: str = "configs/redis.yaml"):
        # 加载配置
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        with open(redis_config_path, "r") as f:
            redis_config = yaml.safe_load(f)
        
        # 初始化Redis客户端
        self.redis = redis.Redis(
            host=redis_config["redis"]["host"],
            port=redis_config["redis"]["port"],
            db=redis_config["redis"]["db"],
            password=redis_config["redis"]["password"],
            decode_responses=True
        )
        
        # 存储向量存储引用
        self.vector_store = vector_store
        
        # 加载文档处理设置
        self.doc_settings = self.config["document_processing"]
        self.supported_formats = self.doc_settings["supported_formats"]
        self.chunk_size = self.doc_settings["chunk_size"]
        self.chunk_overlap = self.doc_settings["chunk_overlap"]
        
        logger.info(f"文档服务初始化完成，支持格式: {self.supported_formats}")
    
    def process_document(self, file: BinaryIO, filename: str, user_id: str,
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理文档文件，提取文本并准备索引"""
        # 验证文件格式
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {ext}. 支持的格式: {self.supported_formats}")
        
        # 生成文档ID和文件哈希
        doc_id = str(uuid.uuid4())
        file_content = file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        file.seek(0)
        
        # 确定MIME类型
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        # 创建文档元数据
        doc_metadata = {
            "id": doc_id,
            "filename": filename,
            "file_extension": ext,
            "mime_type": mime_type,
            "file_size": len(file_content),
            "file_hash": file_hash,
            "upload_date": datetime.now().isoformat(),
            "user_id": user_id,
            "status": "processing",
            "chunks_count": 0
        }
        
        # 添加自定义元数据
        if metadata:
            doc_metadata.update({"custom_metadata": metadata})
        
        # 临时存储文档元数据
        self.redis.set(
            f"doc:{doc_id}:metadata", 
            json.dumps(doc_metadata),
            ex=3600  # 1小时过期
        )
        
        try:
            # 获取适当的处理器
            processor = get_document_processor(ext)
            
            # 提取文本和元数据
            extracted_text, extracted_metadata = processor.process(file)
            
            # 更新元数据
            doc_metadata.update({
                "extracted_metadata": extracted_metadata,
                "text_length": len(extracted_text),
                "status": "chunking"
            })
            
            # 更新Redis
            self.redis.set(
                f"doc:{doc_id}:metadata", 
                json.dumps(doc_metadata),
                ex=3600
            )
            
            # 分块文档
            chunks = self._chunk_document(extracted_text, doc_id)
            
            # 更新元数据
            doc_metadata.update({
                "chunks_count": len(chunks),
                "status": "embedding"
            })
            
            # 更新Redis
            self.redis.set(
                f"doc:{doc_id}:metadata", 
                json.dumps(doc_metadata),
                ex=3600
            )
            
            # 处理文档嵌入和索引
            self._process_embeddings_and_index(chunks, doc_id, doc_metadata)
            
            # 更新最终状态
            doc_metadata["status"] = "indexed"
            self.redis.set(
                f"doc:{doc_id}:metadata", 
                json.dumps(doc_metadata),
                ex=3600
            )
            
            # 返回元数据
            return doc_metadata
            
        except Exception as e:
            # 更新元数据错误
            doc_metadata.update({
                "status": "error",
                "processing_error": str(e)
            })
            
            # 更新Redis
            self.redis.set(
                f"doc:{doc_id}:metadata", 
                json.dumps(doc_metadata),
                ex=3600
            )
            
            logger.error(f"处理文档 {filename} (ID: {doc_id}) 错误: {str(e)}")
            raise Exception(f"文档处理失败: {str(e)}")
    
    def _chunk_document(self, text: str, doc_id: str) -> List[Dict[str, Any]]:
        """将文档文本分成块"""
        chunks = []
        
        # 基于字符的分块，带重叠
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # 计算结束位置
            end = min(start + self.chunk_size, len(text))
            
            # 如果不是最后一块，尝试找到自然断点
            if end < len(text):
                # 尝试找到句子断点（句号、问号、感叹号）
                for i in range(min(100, end - start)):
                    if text[end - i - 1] in ['.', '?', '!', '\n'] and text[end - i] in [' ', '\n']:
                        end = end - i
                        break
            
            # 提取块文本
            chunk_text = text[start:end]
            
            # 创建块元数据
            chunk = {
                "chunk_id": f"{doc_id}_{chunk_id}",
                "document_id": doc_id,
                "text": chunk_text,
                "start_char": start,
                "end_char": end,
                "length": len(chunk_text)
            }
            
            chunks.append(chunk)
            
            # 移动到下一块位置，考虑重叠
            start = end - self.chunk_overlap
            chunk_id += 1
            
            # 确保我们有进展
            if start >= end:
                start = end
        
        return chunks
    
    def _process_embeddings_and_index(self, chunks: List[Dict[str, Any]], 
                                     doc_id: str, doc_metadata: Dict[str, Any]):
        """处理文档块嵌入和索引"""
        # 提取文本列表
        texts = [chunk["text"] for chunk in chunks]
        
        # 批量获取嵌入
        batch_size = self.config["embedding"]["batch_size"]
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = get_embeddings(batch_texts)
            all_embeddings.extend(batch_embeddings)
        
        # 准备向量和有效载荷
        vectors = all_embeddings
        payloads = chunks
        chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        
        # 存储在向量存储中
        self.vector_store.add_documents(
            vectors=vectors,
            payloads=payloads,
            ids=chunk_ids
        )
        
        # 存储文档元数据
        doc_vector = all_embeddings[0] if all_embeddings else [0.0] * 768  # 默认向量大小
        self.vector_store.add_documents(
            vectors=[doc_vector],
            payloads=[doc_metadata],
            ids=[doc_id],
            collection_name=self.vector_store.metadata_collection
        ) 

    def get_document_metadata(self, document_id: str) -> Dict[str, Any]:
    """
    获取文档元数据
    
    Args:
        document_id: 文档ID
        
    Returns:
        Dict[str, Any]: 文档元数据
        
    Raises:
        ValueError: 如果文档不存在
    """
    try:
        # 从Redis检查缓存
        cached_metadata = self.redis.get(f"doc:{document_id}:metadata")
        if cached_metadata:
            return json.loads(cached_metadata)
        
        # 如果缓存中没有，从向量存储中获取
        results = self.vector_store.query(
            query_vector=[0.0] * 768,  # 使用空向量
            limit=1,
            filter_={"id": document_id},
            collection_name=self.vector_store.metadata_collection
        )
        
        if not results:
            raise ValueError(f"文档 {document_id} 不存在")
        
        # 返回文档元数据
        return results[0]["payload"]
        
    except Exception as e:
        logger.error(f"获取文档元数据错误: {str(e)}")
        raise Exception(f"获取文档元数据失败: {str(e)}")

def get_all_documents(self, filters: Dict[str, Any], limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    """
    获取所有文档的元数据
    
    Args:
        filters: 过滤条件
        limit: 最大返回数量
        offset: 偏移量
        
    Returns:
        Tuple[List[Dict[str, Any]], int]: 文档元数据列表和总数
    """
    try:
        # 从向量存储中获取所有文档
        results = self.vector_store.query(
            query_vector=[0.0] * 768,  # 使用空向量
            limit=limit + offset,
            filter_=filters,
            collection_name=self.vector_store.metadata_collection
        )
        
        # 获取总数
        total_count = len(results)
        
        # 应用偏移和限制
        results = results[offset:offset+limit]
        
        # 提取元数据
        documents = [result["payload"] for result in results]
        
        return documents, total_count
        
    except Exception as e:
        logger.error(f"获取所有文档错误: {str(e)}")
        raise Exception(f"获取文档列表失败: {str(e)}")

def delete_document(self, document_id: str) -> bool:
    """
    删除文档及其索引
    
    Args:
        document_id: 文档ID
        
    Returns:
        bool: 操作是否成功
        
    Raises:
        ValueError: 如果文档不存在
    """
    try:
        # 检查文档是否存在
        doc_metadata = self.get_document_metadata(document_id)
        
        # 删除文档块
        self.vector_store.client.delete(
            collection_name=self.vector_store.default_collection,
            points_selector=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="document_id",
                        match=rest.MatchValue(value=document_id)
                    )
                ]
            )
        )
        
        # 删除文档元数据
        self.vector_store.client.delete(
            collection_name=self.vector_store.metadata_collection,
            points_selector=rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="id",
                        match=rest.MatchValue(value=document_id)
                    )
                ]
            )
        )
        
        # 删除Redis缓存
        self.redis.delete(f"doc:{document_id}:metadata")
        
        # 创建一个删除文档的后台任务来清理相关资源
        task_id = str(uuid.uuid4())
        task_data = {
            "type": "document_cleanup",
            "task_id": task_id,
            "document_id": document_id,
            "created_at": time.time()
        }
        
        # 将任务添加到队列
        self.redis.rpush("task_queue", json.dumps(task_data))
        
        return True
        
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(f"删除文档错误: {str(e)}")
        raise Exception(f"删除文档失败: {str(e)}")

def reindex_document(self, document_id: str) -> str:
    """
    重新索引文档
    
    Args:
        document_id: 文档ID
        
    Returns:
        str: 任务ID
        
    Raises:
        ValueError: 如果文档不存在
    """
    try:
        # 检查文档是否存在
        doc_metadata = self.get_document_metadata(document_id)
        
        # 创建一个重新索引任务
        task_id = str(uuid.uuid4())
        task_data = {
            "type": "indexing",
            "task_id": task_id,
            "document_ids": [document_id],
            "user_id": doc_metadata.get("user_id", ""),
            "rebuild_all": False,
            "created_at": time.time()
        }
        
        # 将任务添加到队列
        self.redis.rpush("task_queue", json.dumps(task_data))
        
        # 更新文档状态
        doc_metadata["status"] = "reindexing"
        self.redis.set(
            f"doc:{document_id}:metadata", 
            json.dumps(doc_metadata),
            ex=3600
        )
        
        # 存储任务状态
        self.redis.hset(
            f"task:{task_id}",
            mapping={
                "status": "queued",
                "type": "indexing",
                "document_ids": json.dumps([document_id]),
                "created_at": time.time(),
                "user_id": doc_metadata.get("user_id", "")
            }
        )
        
        return task_id
        
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(f"重新索引文档错误: {str(e)}")
        raise Exception(f"重新索引文档失败: {str(e)}")

def get_task_status(self, task_id: str) -> Dict[str, Any]:
    """
    获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict[str, Any]: 任务状态信息
        
    Raises:
        ValueError: 如果任务不存在
    """
    try:
        # 从Redis获取任务状态
        task_data = self.redis.hgetall(f"task:{task_id}")
        
        if not task_data:
            raise ValueError(f"任务 {task_id} 不存在")
        
        # 转换某些字段
        if "document_ids" in task_data and task_data["document_ids"]:
            task_data["document_ids"] = json.loads(task_data["document_ids"])
        
        if "created_at" in task_data and task_data["created_at"]:
            task_data["created_at"] = float(task_data["created_at"])
        
        if "completed_at" in task_data and task_data["completed_at"]:
            task_data["completed_at"] = float(task_data["completed_at"])
        
        return task_data
        
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(f"获取任务状态错误: {str(e)}")
        raise Exception(f"获取任务状态失败: {str(e)}")