 import os
import logging
import yaml
from typing import Dict, List, Optional, Any
import redis
import json
import time
from .vector_store import VectorStore
from .llm_service import LLMService

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, vector_store: VectorStore, llm_service: LLMService,
                redis_config_path: str = "configs/redis.yaml"):
        # 加载Redis配置
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
        
        # 缓存TTL
        self.cache_ttl = redis_config["cache"]["ttl"]
        
        # 存储服务
        self.vector_store = vector_store
        self.llm_service = llm_service
        
        logger.info("搜索服务初始化完成")
    
    def search(self, query: str, user_id: Optional[str] = None, limit: int = 10,
              use_hybrid: bool = True, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """使用查询字符串搜索向量存储"""
        # 生成缓存键
        cache_key = f"search:{hash(query)}:{user_id or 'all'}:{limit}:{use_hybrid}:{hash(str(filters))}"
        
        # 检查缓存
        cached_results = self.redis.get(cache_key)
        if cached_results:
            logger.info(f"缓存命中: {query}")
            return json.loads(cached_results)
        
        try:
            # 生成查询嵌入
            start_time = time.time()
            query_embedding = self.llm_service.get_embedding(query)
            embedding_time = time.time() - start_time
            logger.debug(f"生成查询嵌入耗时: {embedding_time:.3f}秒")
            
            # 准备过滤器
            search_filter = self._prepare_filter(user_id, filters)
            
            # 执行向量搜索
            start_time = time.time()
            semantic_results = self.vector_store.query(
                query_vector=query_embedding,
                limit=limit,
                filter_=search_filter
            )
            vector_time = time.time() - start_time
            logger.debug(f"向量搜索完成，耗时: {vector_time:.3f}秒")
            
            # 格式化结果
            results = self._format_search_results(semantic_results)
            
            # 缓存结果
            self.redis.set(cache_key, json.dumps(results), ex=self.cache_ttl)
            
            return results
                
        except Exception as e:
            logger.error(f"搜索查询'{query}'时出错: {str(e)}")
            raise Exception(f"搜索失败: {str(e)}")
    
    def _prepare_filter(self, user_id: Optional[str] = None, 
                       additional_filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """准备向量搜索的过滤器"""
        filter_dict = {}
        filter_conditions = []
        
        # 添加用户过滤器
        if user_id:
            filter_conditions.append({
                "key": "user_id",
                "match": {
                    "value": user_id
                }
            })
        
        # 添加额外过滤器
        if additional_filters:
            for key, value in additional_filters.items():
                if isinstance(value, list):
                    # 处理列表值（OR条件）
                    or_conditions = []
                    for val in value:
                        or_conditions.append({
                            "key": key,
                            "match": {
                                "value": val
                            }
                        })
                    
                    if or_conditions:
                        filter_conditions.append({
                            "should": or_conditions
                        })
                else:
                    # 处理单个值
                    filter_conditions.append({
                        "key": key,
                        "match": {
                            "value": value
                        }
                    })
        
        # 将所有条件与AND逻辑组合
        if filter_conditions:
            filter_dict = {
                "must": filter_conditions
            }
        
        return filter_dict
    
    def _format_search_results(self, vector_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将向量搜索结果格式化为标准格式"""
        formatted_results = []
        
        for result in vector_results:
            # 提取基本信息
            result_id = result["id"]
            score = result["score"]
            payload = result["payload"]
            
            # 创建格式化结果
            formatted_result = {
                "id": result_id,
                "score": score,
                "text": payload.get("text", ""),
                "metadata": {
                    "document_id": payload.get("document_id", ""),
                    "chunk_id": payload.get("chunk_id", ""),
                    "filename": payload.get("filename", ""),
                    "position": {
                        "start": payload.get("start_char", 0),
                        "end": payload.get("end_char", 0)
                    }
                }
            }
            
            formatted_results.append(formatted_result)
        
        return formatted_results
