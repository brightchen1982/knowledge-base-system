import os
import logging
from typing import Dict, Any, Tuple, List, Optional, BinaryIO
import tempfile
import fitz  # PyMuPDF
import re
from .base import DocumentProcessor, register_processor

logger = logging.getLogger(__name__)

@register_processor(extensions=['.pdf'])
class PDFProcessor(DocumentProcessor):
    """PDF文档处理器"""
    
    def process(self, file: BinaryIO) -> Tuple[str, Dict[str, Any]]:
        """
        处理PDF文件，提取文本和元数据
        
        Args:
            file: PDF文件对象
            
        Returns:
            Tuple[str, Dict[str, Any]]: 提取的文本和元数据
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # 写入数据
            tmp.write(file.read())
            file.seek(0)  # 重置文件指针
            tmp_path = tmp.name
        
        try:
            # 打开PDF文档
            doc = fitz.open(tmp_path)
            
            # 提取元数据
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "keywords": doc.metadata.get("keywords", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", ""),
                "page_count": len(doc),
            }
            
            # 提取文本
            extracted_text = ""
            for page_num, page in enumerate(doc):
                # 获取页面文本
                page_text = page.get_text()
                
                # 清理文本
                page_text = self._clean_text(page_text)
                
                # 添加页码标记
                extracted_text += f"\n--- 页 {page_num + 1} ---\n{page_text}\n"
            
            # 提取目录（TOC）
            toc = doc.get_toc()
            if toc:
                toc_data = []
                for level, title, page in toc:
                    toc_data.append({
                        "level": level,
                        "title": title,
                        "page": page
                    })
                metadata["toc"] = toc_data
            
            # 处理图像
            image_count = 0
            for page_num, page in enumerate(doc):
                image_list = page.get_images(full=True)
                image_count += len(image_list)
            
            metadata["image_count"] = image_count
            
            return extracted_text, metadata
            
        except Exception as e:
            logger.error(f"处理PDF时出错: {str(e)}")
            raise Exception(f"PDF处理失败: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _clean_text(self, text: str) -> str:
        """清理提取的文本"""
        # 删除多余的空格
        text = re.sub(r'\s+', ' ', text)
        
        # 删除多余的换行符
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 删除页眉页脚（假设出现在每页的前几行和后几行）
        lines = text.split('\n')
        if len(lines) > 6:
            # 保留中间部分，去掉可能的页眉页脚
            text = '\n'.join(lines)
        
        return text 
