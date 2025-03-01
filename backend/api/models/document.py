from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    INDEXED = "indexed"
    ERROR = "error"

class DocumentMetadata(BaseModel):
    """文档元数据模型"""
    id: str
    filename: str
    file_extension: str
    mime_type: str
    file_size: int
    file_hash: str
    upload_date: datetime
    user_id: str
    status: DocumentStatus
    chunks_count: Optional[int] = 0
    text_length: Optional[int] = 0
    processing_error: Optional[str] = None
    extracted_metadata: Optional[Dict[str, Any]] = None
    custom_metadata: Optional[Dict[str, Any]] = None

class DocumentResponse(BaseModel):
    """文档响应模型"""
    document: DocumentMetadata
    message: Optional[str] = None

class DocumentListResponse(BaseModel):
    """文档列表响应模型"""
    documents: List[DocumentMetadata]
    total: int
    limit: int
    offset: int

class DocumentStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: Dict[str, Any]