import os
import logging
from typing import Dict, Any, Tuple, List, Optional, BinaryIO
import tempfile
from bs4 import BeautifulSoup
import re
from .base import DocumentProcessor, register_processor

logger = logging.getLogger(__name__)

@register_processor(extensions=['.html', '.htm'])
class HtmlProcessor(DocumentProcessor):
    """HTML文档处理器"""
    
    def process(self, file: BinaryIO) -> Tuple[str, Dict[str, Any]]:
        """
        处理HTML文件，提取文本和元数据
        
        Args:
            file: HTML文件对象
            
        Returns:
            Tuple[str, Dict[str, Any]]: 提取的文本和元数据
        """
        # 读取文件内容
        content = file.read().decode('utf-8', errors='replace')
        
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # 提取元数据
            metadata = {
                "title": self._get_title(soup),
                "description": self._get_meta_content(soup, "description"),
                "keywords": self._get_meta_content(soup, "keywords"),
                "author": self._get_meta_content(soup, "author"),
                "links_count": len(soup.find_all('a')),
                "images_count": len(soup.find_all('img')),
                "tables_count": len(soup.find_all('table')),
                "scripts_count": len(soup.find_all('script')),
                "styles_count": len(soup.find_all('style')),
            }
            
            # 提取并清理文本
            extracted_text = self._extract_text(soup)
            
            return extracted_text, metadata
            
        except Exception as e:
            logger.error(f"处理HTML文件时出错: {str(e)}")
            raise Exception(f"HTML处理失败: {str(e)}")
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """获取HTML标题"""
        title_tag = soup.find('title')
        return title_tag.get_text() if title_tag else ""
    
    def _get_meta_content(self, soup: BeautifulSoup, meta_name: str) -> str:
        """获取指定名称的meta标签内容"""
        meta_tag = soup.find('meta', attrs={'name': meta_name})
        if meta_tag and meta_tag.get('content'):
            return meta_tag.get('content')
        return ""
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """提取并清理HTML文本内容"""
        # 删除脚本和样式标签
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        
        # 提取文本
        text = soup.get_text()
        
        # 处理标题
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_level = int(heading.name[1])
            heading_text = heading.get_text().strip()
            text = text.replace(heading_text, f"\n{'#' * heading_level} {heading_text}\n")
        
        # 处理列表
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li'):
                li_text = li.get_text().strip()
                text = text.replace(li_text, f"- {li_text}")
        
        # 处理有序列表
        for ol in soup.find_all('ol'):
            for i, li in enumerate(ol.find_all('li')):
                li_text = li.get_text().strip()
                text = text.replace(li_text, f"{i+1}. {li_text}")
        
        # 清理空白
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text