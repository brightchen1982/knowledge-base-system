from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    user_id: Optional[str] = None
    limit: int = 10
    offset: int = 0
    use_hybrid: bool = True
    filters: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    """搜索结果项模型"""
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    """搜索响应模型"""
    results: List[SearchResult]
    count: int

class RelatedQueryResponse(BaseModel):
    """相关查询响应模型"""
    queries: List[str]
    count: int