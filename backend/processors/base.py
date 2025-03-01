import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Optional, BinaryIO, Type

logger = logging.getLogger(__name__)

class DocumentProcessor(ABC):
    """文档处理器基类，定义处理接口"""
    
    @abstractmethod
    def process(self, file: BinaryIO) -> Tuple[str, Dict[str, Any]]:
        """
        处理文档文件
        
        Args:
            file: 文件对象
            
        Returns:
            Tuple[str, Dict[str, Any]]: 提取的文本和元数据
        """
        pass

# 存储注册的处理器
_PROCESSORS: Dict[str, Type[DocumentProcessor]] = {}

def register_processor(extensions: List[str]):
    """文档处理器注册装饰器"""
    def decorator(processor_class: Type[DocumentProcessor]):
        for ext in extensions:
            _PROCESSORS[ext.lower()] = processor_class
        return processor_class
    return decorator

def get_document_processor(extension: str) -> DocumentProcessor:
    """
    根据文件扩展名获取适当的处理器
    
    Args:
        extension: 文件扩展名（包含点，如'.pdf'）
        
    Returns:
        DocumentProcessor: 文档处理器实例
    
    Raises:
        ValueError: 如果找不到适用于该扩展名的处理器
    """
    ext = extension.lower()
    if ext not in _PROCESSORS:
        raise ValueError(f"未找到支持的处理器: {ext}")
    
    # 实例化处理器
    return _PROCESSORS[ext]() 
