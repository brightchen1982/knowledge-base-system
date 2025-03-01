import os
import logging
from typing import Dict, Any, Tuple, List, Optional, BinaryIO
import tempfile
import pandas as pd
from .base import DocumentProcessor, register_processor

logger = logging.getLogger(__name__)

@register_processor(extensions=['.xlsx', '.xls'])
class ExcelProcessor(DocumentProcessor):
    """Excel文档处理器"""
    
    def process(self, file: BinaryIO) -> Tuple[str, Dict[str, Any]]:
        """
        处理Excel文件，提取文本和元数据
        
        Args:
            file: Excel文件对象
            
        Returns:
            Tuple[str, Dict[str, Any]]: 提取的文本和元数据
        """
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            # 写入数据
            tmp.write(file.read())
            file.seek(0)  # 重置文件指针
            tmp_path = tmp.name
        
        try:
            # 使用pandas读取Excel文件
            excel_file = pd.ExcelFile(tmp_path)
            sheet_names = excel_file.sheet_names
            
            # 提取元数据
            metadata = {
                "sheet_count": len(sheet_names),
                "sheet_names": sheet_names,
                "file_path": tmp_path,
            }
            
            # 提取文本
            extracted_text = ""
            
            # 遍历所有工作表
            for sheet_index, sheet_name in enumerate(sheet_names):
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # 添加工作表标题
                extracted_text += f"\n--- 工作表: {sheet_name} ---\n\n"
                
                # 处理列名（表头）
                header_row = "| " + " | ".join(str(col) for col in df.columns) + " |\n"
                separator = "|" + "---|" * len(df.columns) + "\n"
                extracted_text += header_row + separator
                
                # 处理数据行
                for _, row in df.iterrows():
                    row_text = "| " + " | ".join(str(cell) if str(cell) != "nan" else "" for cell in row) + " |\n"
                    extracted_text += row_text
                
                extracted_text += "\n"
                
                # 添加工作表级元数据
                metadata[f"sheet_{sheet_index}_rows"] = len(df)
                metadata[f"sheet_{sheet_index}_columns"] = len(df.columns)
            
            # 统计总行数和列数
            total_cells = sum(metadata.get(f"sheet_{i}_rows", 0) * metadata.get(f"sheet_{i}_columns", 0) 
                             for i in range(len(sheet_names)))
            metadata["total_cells"] = total_cells
            
            return extracted_text, metadata
            
        except Exception as e:
            logger.error(f"处理Excel文件时出错: {str(e)}")
            raise Exception(f"Excel处理失败: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)