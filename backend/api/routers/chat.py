from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import logging
import json
import uuid
import asyncio
from ..deps.auth import get_current_user, get_token_from_websocket
from ..models.user import User
from ..models.chat import ChatRequest, ChatResponse
from ...services.search_service import SearchService
from ...services.llm_service import LLMService
from ...services.vector_store import VectorStore
from ...services.graphrag_service import GraphRAGService

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化服务
vector_store = VectorStore()
llm_service = LLMService()
search_service = SearchService(vector_store, llm_service)
graphrag_service = GraphRAGService(vector_store, llm_service)

# 存储活跃的WebSocket连接
active_connections = {}

@router.post("/", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """标准聊天请求"""
    try:
        # 确定是否需要RAG
        use_rag = request.use_rag if request.use_rag is not None else True
        
        if use_rag:
            # 使用GraphRAG提供上下文
            context = graphrag_service.get_context_for_query(
                query=request.message,
                user_id=current_user.id if request.user_specific else None,
                document_ids=request.document_ids,
                max_results=request.max_context_chunks
            )
            
            # 生成带上下文的提示
            augmented_prompt = f"""请根据以下上下文和相关信息回答问题。如果上下文信息不足以回答问题，请明确指出。

上下文信息:
{context}

用户问题: {request.message}"""
            
            # 调用LLM生成回复
            response = llm_service.generate(augmented_prompt, system_prompt=request.system_prompt)
            answer = response["response"]
        else:
            # 直接调用LLM
            response = llm_service.generate(request.message, system_prompt=request.system_prompt)
            answer = response["response"]
        
        return {
            "message_id": str(uuid.uuid4()),
            "answer": answer,
            "sources": [{"id": s["id"], "text": s["text"], "metadata": s["metadata"]} for s in context] if use_rag else []
        }
        
    except Exception as e:
        logger.error(f"聊天处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail="处理聊天请求失败")

@router.post("/stream", response_class=StreamingResponse)
async def stream_chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """流式聊天响应"""
    try:
        # 确定是否需要RAG
        use_rag = request.use_rag if request.use_rag is not None else True
        context = []
        
        if use_rag:
            # 使用GraphRAG提供上下文
            context = graphrag_service.get_context_for_query(
                query=request.message,
                user_id=current_user.id if request.user_specific else None,
                document_ids=request.document_ids,
                max_results=request.max_context_chunks
            )
            
            # 生成带上下文的提示
            augmented_prompt = f"""请根据以下上下文和相关信息回答问题。如果上下文信息不足以回答问题，请明确指出。

上下文信息:
{context}

用户问题: {request.message}"""
            prompt = augmented_prompt
        else:
            prompt = request.message
        
        # 创建一个流式响应生成器
        async def generate():
            # 发送元数据和来源信息
            message_id = str(uuid.uuid4())
            metadata = {
                "message_id": message_id,
                "sources": [{"id": s["id"], "text": s["text"], "metadata": s["metadata"]} for s in context] if use_rag else []
            }
            yield f"data: {json.dumps({'type': 'metadata', 'content': metadata})}\n\n"
            
            # 流式生成内容
            for chunk in llm_service.generate_stream(prompt, system_prompt=request.system_prompt):
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
            
            # 发送完成信号
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"流式聊天处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail="处理聊天请求失败") 
