 import os
import logging
import yaml
from typing import List, Optional, Dict, Any
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from .model import get_embeddings

logger = logging.getLogger(__name__)

class BatchProcessor:
    """批量处理嵌入向量的工具类"""
    
    def __init__(self, config_path: str = "configs/worker.yaml"):
        # 加载配置
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        # 获取批处理设置
        batch_settings = self.config["embedding"]
        self.batch_size = batch_settings["batch_size"]
        self.max_workers = batch_settings["max_workers"]
        
        logger.info(f"嵌入批处理器初始化完成，批大小: {self.batch_size}, 最大工作线程: {self.max_workers}")
    
    def process_in_batches(self, texts: List[str]) -> List[List[float]]:
        """
        批量处理文本嵌入
        
        Args:
            texts: 要处理的文本列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        all_embeddings = []
        
        # 根据批大小拆分文本
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i+self.batch_size]
            logger.info(f"处理批次 {i//self.batch_size + 1}/{(len(texts) + self.batch_size - 1)//self.batch_size}, 大小: {len(batch)}")
            
            # 获取当前批次的嵌入
            batch_embeddings = get_embeddings(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    def process_in_parallel(self, texts: List[str]) -> List[List[float]]:
        """
        并行批量处理文本嵌入
        
        Args:
            texts: 要处理的文本列表
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        # 根据批大小拆分文本
        batches = [texts[i:i+self.batch_size] for i in range(0, len(texts), self.batch_size)]
        logger.info(f"拆分为 {len(batches)} 个批次进行并行处理")
        
        # 并行处理
        all_embeddings = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有批次任务
            futures = [executor.submit(get_embeddings, batch) for batch in batches]
            
            # 收集结果
            for future in futures:
                result = future.result()
                all_embeddings.extend(result)
        
        # 确保结果顺序与输入一致
        return all_embeddings
