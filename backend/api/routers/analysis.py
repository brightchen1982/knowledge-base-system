 from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
from ..deps.auth import get_current_user
from ..models.user import User
from ..models.analysis import (
    DocumentAnalysisRequest,
    DocumentAnalysisResponse,
    TextAnalysisRequest,
    TextAnalysisResponse,
    PredictionRequest,
    PredictionResponse
)
from ...services.llm_service import LLMService
from ...services.vector_store import VectorStore
from ...services.search_service import SearchService

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化服务
vector_store = VectorStore()
llm_service = LLMService()
search_service = SearchService(vector_store, llm_service)

@router.post("/document", response_model=DocumentAnalysisResponse)
async def analyze_document(
    request: DocumentAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """分析文档内容"""
    try:
        # 创建文档过滤器
        filters = {"document_id": request.document_id}
        
        # 获取文档内容
        doc_chunks = search_service.search(
            query="",  # 空查询，获取所有内容
            user_id=current_user.id,
            limit=100,  # 限制返回块数
            filters=filters
        )
        
        # 提取文档文本
        doc_text = " ".join([chunk["text"] for chunk in doc_chunks])
        
        # 生成分析提示
        analysis_prompt = f"""请分析以下文档内容，重点关注{request.focus_areas}。请给出关键点、主要观点和结论。

文档内容:
{doc_text[:8000]}  # 防止提示过长

分析要求: {request.instructions if request.instructions else "提供全面分析"}"""

        # 调用LLM生成分析
        response = llm_service.generate(analysis_prompt)
        analysis = response["response"]
        
        return {
            "document_id": request.document_id,
            "analysis": analysis,
            "summary": analysis[:200] + "..." if len(analysis) > 200 else analysis
        }
        
    except Exception as e:
        logger.error(f"文档分析错误: {str(e)}")
        raise HTTPException(status_code=500, detail="文档分析失败")

@router.post("/text", response_model=TextAnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """分析任意文本内容"""
    try:
        # 生成分析提示
        analysis_prompt = f"""请分析以下文本内容，重点关注{request.focus_areas}。请给出关键点、主要观点和结论。

文本内容:
{request.text[:8000]}  # 防止提示过长

分析要求: {request.instructions if request.instructions else "提供全面分析"}"""

        # 调用LLM生成分析
        response = llm_service.generate(analysis_prompt)
        analysis = response["response"]
        
        return {
            "analysis": analysis,
            "summary": analysis[:200] + "..." if len(analysis) > 200 else analysis
        }
        
    except Exception as e:
        logger.error(f"文本分析错误: {str(e)}")
        raise HTTPException(status_code=500, detail="文本分析失败")

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """基于历史数据进行预测"""
    try:
        # 准备预测提示
        prediction_prompt = f"""根据以下历史数据和上下文，请预测{request.target}。

历史数据:
{request.historical_data[:4000]}  # 防止提示过长

上下文信息:
{request.context[:4000] if request.context else "无额外上下文信息"}

预测目标: {request.target}
预测说明: {request.instructions if request.instructions else "提供合理预测"}"""

        # 调用LLM生成预测
        response = llm_service.generate(prediction_prompt)
        prediction_result = response["response"]
        
        return {
            "prediction": prediction_result,
            "confidence": "中等",  # 假设的置信度，实际上需要更复杂的计算
            "factors": []  # 影响因素，可以通过二次分析提取
        }
        
    except Exception as e:
        logger.error(f"预测错误: {str(e)}")
        raise HTTPException(status_code=500, detail="生成预测失败")
