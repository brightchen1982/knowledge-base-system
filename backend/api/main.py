import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yaml
from .routers import documents, search, chat, analysis
from .core.config import Settings

# 加载配置
config_path = os.getenv("API_CONFIG_PATH", "configs/api.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

settings = Settings(**config)

# 设置日志
logging.basicConfig(
    level=getattr(logging, settings.server.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 初始化FastAPI应用
app = FastAPI(
    title="知识库系统API",
    description="高性能本地知识库系统的API",
    version="1.0.0",
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
)

# 包含路由器
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "message": "知识库系统API正在运行", 
        "docs_url": "/docs", 
        "version": app.version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.server.host, 
        port=settings.server.port,
        workers=settings.server.workers
    )
