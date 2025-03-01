from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DocumentAnalysisRequest(BaseModel):
    """文档分析请求模型"""
    document_id: str
    focus_areas: str = "关键数据点和趋势"
    instructions: Optional[str] = None

class DocumentAnalysisResponse(BaseModel):
    """文档分析响应模型"""
    document_id: str
    analysis: str
    summary: str

class TextAnalysisRequest(BaseModel):
    """文本分析请求模型"""
    text: str
    focus_areas: str = "关键点和主题"
    instructions: Optional[str] = None

class TextAnalysisResponse(BaseModel):
    """文本分析响应模型"""
    analysis: str
    summary: str

class PredictionRequest(BaseModel):
    """预测请求模型"""
    historical_data: str
    target: str
    context: Optional[str] = None
    instructions: Optional[str] = None

class PredictionFactor(BaseModel):
    """预测影响因素模型"""
    name: str
    impact: str  # 'positive', 'negative', 'neutral'
    weight: float  # 0.0 to 1.0

class PredictionResponse(BaseModel):
    """预测响应模型"""
    prediction: str
    confidence: str  # 'high', 'medium', 'low'
    factors: List[PredictionFactor] = []