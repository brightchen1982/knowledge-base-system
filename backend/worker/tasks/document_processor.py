import os
import logging
from typing import Dict, Any, List, BinaryIO
import tempfile
import time
import uuid
from ...services.document_service import DocumentService
from ...services.vector_store import VectorStore

logger = logging.getLogger(__name__)

class DocumentProcessorTask:
    """文档处理任务类"""
    
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service
    
    def process(self, file_path: str, filename: str, user_id: str, 
               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理文档文件
        
        Args:
            file_path: 临时文件路径
            filename: 原始文件名
            user_id: 用户ID
            metadata: 可选的元数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        start_time = time.time()
        logger.info(f"开始处理文档: {filename}")
        
        try:
            # 打开文件
            with open(file_path, 'rb') as file:
                # 处理文档
                result = self.document_service.process_document(
                    file=file,
                    filename=filename,
                    user_id=user_id,
                    metadata=metadata
                )
            
            processing_time = time.time() - start_time
            logger.info(f"文档处理完成: {filename}, 耗时: {processing_time:.2f}秒")
            
            return {
                "success": True,
                "document_id": result["id"],
                "processing_time": processing_time,
                "chunks_count": result["chunks_count"]
            }
            
        except Exception as e:
            logger.error(f"处理文档{filename}时出错: {str(e)}")
            
            processing_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time
            }
        finally:
            # 删除临时文件
            if os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except Exception as e:
                    logger.warning(f"删除临时文件{file_path}失败: {str(e)}")