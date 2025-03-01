 from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import logging
import tempfile
import os
import uuid
from ..deps.auth import get_current_user
from ..models.user import User
from ..models.document import DocumentResponse, DocumentListResponse, DocumentStatusResponse
from ...services.document_service import DocumentService
from ...services.vector_store import VectorStore

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化服务
vector_store = VectorStore()
document_service = DocumentService(vector_store)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """上传文档进行处理和索引"""
    try:
        # 解析元数据
        metadata_dict = json.loads(metadata) if metadata else {}
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            # 写入上传的文件内容
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 创建任务ID
            task_id = str(uuid.uuid4())
            
            # 提交处理任务
            doc_metadata = document_service.process_document(
                file=open(temp_file_path, 'rb'),
                filename=file.filename,
                user_id=current_user.id,
                metadata=metadata_dict
            )
            
            return JSONResponse(
                status_code=202,  # Accepted
                content={"message": "文档上传已接受处理", "document": doc_metadata, "task_id": task_id}
            )
        finally:
            # 删除临时文件
            os.unlink(temp_file_path)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"上传文档错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取文档状态和元数据"""
    try:
        doc_metadata = document_service.get_document_metadata(document_id)
        
        # 检查授权
        if doc_metadata.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此文档")
        
        return {"document": doc_metadata}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取文档 {document_id} 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """列出当前用户的所有文档"""
    try:
        # 准备过滤器
        filters = {"user_id": current_user.id}
        if category:
            filters["category"] = category
        if status:
            filters["status"] = status
        
        # 获取文档列表
        documents, total_count = document_service.get_all_documents(
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        return {"documents": documents, "total": total_count, "limit": limit, "offset": offset}
        
    except Exception as e:
        logger.error(f"列出文档错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除文档及其索引"""
    try:
        # 检查文档所有权
        doc_metadata = document_service.get_document_metadata(document_id)
        if doc_metadata.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="无权删除此文档")
        
        # 删除文档
        document_service.delete_document(document_id)
        
        return {"message": f"文档 {document_id} 已成功删除"}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除文档 {document_id} 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")

@router.post("/{document_id}/reindex")
async def reindex_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """重新索引文档"""
    try:
        # 检查文档所有权
        doc_metadata = document_service.get_document_metadata(document_id)
        if doc_metadata.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="无权重新索引此文档")
        
        # 创建重新索引任务
        task_id = document_service.reindex_document(document_id)
        
        return {"message": f"文档 {document_id} 重新索引任务已创建", "task_id": task_id}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"重新索引文档 {document_id} 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"重新索引文档失败: {str(e)}")

@router.get("/task/{task_id}", response_model=DocumentStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取文档处理任务状态"""
    try:
        task_status = document_service.get_task_status(task_id)
        
        # 检查任务所有权
        if task_status.get("user_id") and task_status.get("user_id") != current_user.id:
            raise HTTPException(status_code=403, detail="无权查看此任务状态")
        
        return {"task_id": task_id, "status": task_status}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取任务 {task_id} 状态错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")
