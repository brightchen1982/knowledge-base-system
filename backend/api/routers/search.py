from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
from ..deps.auth import get_current_user
from ..models.user import User
from ..models.search import SearchRequest, SearchResponse
from ...services.search_service import SearchService
from ...services.llm_service import LLMService
from ...services.vector_store import VectorStore

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化服务
vector_store = VectorStore()
llm_service = LLMService()
search_service = SearchService(vector_store, llm_service)

@router.post("/", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """搜索文档库"""
    try:
        results = search_service.search(
            query=request.query,
            user_id=current_user.id,
            limit=request.limit,
            use_hybrid=request.use_hybrid,
            filters=request.filters
        )
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        logger.error(f"搜索错误: {str(e)}")
        raise HTTPException(status_code=500, detail="搜索执行失败")

@router.get("/documents/{document_id}", response_model=SearchResponse)
async def search_within_document(
    document_id: str,
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """在特定文档内搜索"""
    try:
        # 创建文档过滤器
        filters = {"document_id": document_id}
        
        results = search_service.search(
            query=query,
            user_id=current_user.id,
            limit=limit,
            filters=filters
        )
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        logger.error(f"在文档内搜索错误: {str(e)}")
        raise HTTPException(status_code=500, detail="搜索执行失败") 
