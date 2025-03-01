 import os
import logging
import yaml
from typing import List, Optional, Dict, Any
import numpy as np
from ..services.llm_service import LLMService

logger = logging.getLogger(__name__)

# 全局LLM服务实例
_llm_service = None

def get_llm_service() -> LLMService:
    """获取LLM服务单例"""
    global _llm_service
    if _llm_service is None:
        config_path = os.getenv("OLLAMA_CONFIG_PATH", "configs/ollama.yaml")
        _llm_service = LLMService(config_path)
    return _llm_service

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    获取文本列表的向量嵌入
    
    Args:
        texts: 文本列表
        
    Returns:
        List[List[float]]: 嵌入向量列表
    """
    try:
        llm_service = get_llm_service()
        embeddings = []
        
        for text in texts:
            # 截断长文本
            max_length = 8192  # 大多数嵌入模型的最大输入长度
            if len(text) > max_length:
                text = text[:max_length]
            
            # 获取嵌入
            embedding = llm_service.get_embedding(text)
            embeddings.append(embedding)
        
        return embeddings
        
    except Exception as e:
        logger.error(f"获取嵌入向量失败: {str(e)}")
        # 返回零向量作为回退方案
        return [[0.0] * 768] * len(texts)  # 假设维度为768
