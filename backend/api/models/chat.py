from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    system_prompt: Optional[str] = None
    use_rag: Optional[bool] = True
    user_specific: Optional[bool] = True
    document_ids: Optional[List[str]] = None
    max_context_chunks: int = 5
    
class ChatSource(BaseModel):
    """聊天上下文来源模型"""
    id: str
    text: str
    metadata: Dict[str, Any]

class ChatResponse(BaseModel):
    """聊天响应模型"""
    message_id: str
    answer: str
    sources: Optional[List[ChatSource]] = []

class ChatHistoryItem(BaseModel):
    """聊天历史记录项模型"""
    role: str  # 'user' 或 'assistant'
    content: str
    message_id: Optional[str] = None
    timestamp: Optional[float] = None

class ChatSessionResponse(BaseModel):
    """聊天会话响应模型"""
    session_id: str
    history: List[ChatHistoryItem]
    created_at: float
    updated_at: float