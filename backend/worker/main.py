 import os
import logging
import yaml
import time
import redis
import json
from typing import Dict, Any, Optional
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
import threading
from ..services.document_service import DocumentService
from ..services.vector_store import VectorStore
from ..services.llm_service import LLMService
from ..services.graphrag_service import GraphRAGService

# 加载配置
config_path = os.getenv("WORKER_CONFIG_PATH", "configs/worker.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# 加载Redis配置
redis_config_path = os.getenv("REDIS_CONFIG_PATH", "configs/redis.yaml")
with open(redis_config_path, "r") as f:
    redis_config = yaml.safe_load(f)

# 设置日志
logging.basicConfig(
    level=getattr(logging, config["worker"]["log_level"].upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 初始化服务
vector_store = VectorStore()
llm_service = LLMService()
document_service = DocumentService(vector_store)
graphrag_service = GraphRAGService(vector_store, llm_service)

# 初始化Redis
redis_client = redis.Redis(
    host=redis_config["redis"]["host"],
    port=redis_config["redis"]["port"],
    db=redis_config["redis"]["db"],
    password=redis_config["redis"]["password"],
    decode_responses=True
)

# 创建线程池
thread_pool = ThreadPoolExecutor(max_workers=config["worker"]["threads"])

# 运行状态标志
running = True

def process_document_task(task_data: Dict[str, Any]):
    """处理文档任务"""
    try:
        document_id = task_data.get("document_id")
        task_id = task_data.get("task_id")
        
        logger.info(f"处理文档任务: {task_id}, 文档ID: {document_id}")
        
        # 更新任务状态
        redis_client.hset(f"task:{task_id}", "status", "processing")
        
        # 实际处理文档的逻辑
        # 这里通常会从存储中加载临时文件，然后调用document_service的处理方法
        
        # 如果文档处理已在API层完成，这里可以进行额外的优化或后处理
        # 例如，更新知识图谱
        graphrag_service.update_graph(document_id)
        
        # 更新任务状态为完成
        redis_client.hset(f"task:{task_id}", "status", "completed")
        redis_client.hset(f"task:{task_id}", "completed_at", time.time())
        
        logger.info(f"文档任务 {task_id} 处理完成")
        
    except Exception as e:
        logger.error(f"处理文档任务失败: {str(e)}")
        
        # 更新任务状态为失败
        if task_id:
            redis_client.hset(f"task:{task_id}", "status", "failed")
            redis_client.hset(f"task:{task_id}", "error", str(e))

def process_embedding_task(task_data: Dict[str, Any]):
    """处理嵌入任务"""
    try:
        document_id = task_data.get("document_id")
        chunk_ids = task_data.get("chunk_ids", [])
        task_id = task_data.get("task_id")
        
        logger.info(f"处理嵌入任务: {task_id}, 文档ID: {document_id}, 块数: {len(chunk_ids)}")
        
        # 更新任务状态
        redis_client.hset(f"task:{task_id}", "status", "processing")
        
        # 这里实现嵌入处理逻辑
        # 通常是从数据库加载块内容，然后生成嵌入
        
        # 更新任务状态为完成
        redis_client.hset(f"task:{task_id}", "status", "completed")
        redis_client.hset(f"task:{task_id}", "completed_at", time.time())
        
        logger.info(f"嵌入任务 {task_id} 处理完成")
        
    except Exception as e:
        logger.error(f"处理嵌入任务失败: {str(e)}")
        
        # 更新任务状态为失败
        if task_id:
            redis_client.hset(f"task:{task_id}", "status", "failed")
            redis_client.hset(f"task:{task_id}", "error", str(e))

def process_indexing_task(task_data: Dict[str, Any]):
    """处理索引任务"""
    try:
        document_ids = task_data.get("document_ids", [])
        rebuild_all = task_data.get("rebuild_all", False)
        task_id = task_data.get("task_id")
        
        logger.info(f"处理索引任务: {task_id}, 全量重建: {rebuild_all}, 文档数: {len(document_ids)}")
        
        # 更新任务状态
        redis_client.hset(f"task:{task_id}", "status", "processing")
        
        # 如果是全量重建
        if rebuild_all:
            graphrag_service.update_graph()
        else:
            # 为指定文档更新图结构
            for doc_id in document_ids:
                graphrag_service.update_graph(doc_id)
        
        # 更新任务状态为完成
        redis_client.hset(f"task:{task_id}", "status", "completed")
        redis_client.hset(f"task:{task_id}", "completed_at", time.time())
        
        logger.info(f"索引任务 {task_id} 处理完成")
        
    except Exception as e:
        logger.error(f"处理索引任务失败: {str(e)}")
        
        # 更新任务状态为失败
        if task_id:
            redis_client.hset(f"task:{task_id}", "status", "failed")
            redis_client.hset(f"task:{task_id}", "error", str(e))

def poll_tasks():
    """轮询并处理任务队列中的任务"""
    task_types = {
        "document": process_document_task,
        "embedding": process_embedding_task,
        "indexing": process_indexing_task
    }
    
    while running:
        try:
            # 从任务队列中获取任务
            result = redis_client.blpop("task_queue", timeout=1)
            if result is None:
                continue
                
            # 解析任务数据
            _, task_json = result
            task_data = json.loads(task_json)
            
            # 获取任务类型
            task_type = task_data.get("type")
            task_id = task_data.get("task_id")
            
            if task_type in task_types:
                # 提交任务到线程池
                thread_pool.submit(task_types[task_type], task_data)
            else:
                logger.warning(f"未知任务类型: {task_type}, 任务ID: {task_id}")
            
        except Exception as e:
            logger.error(f"轮询任务时出错: {str(e)}")
            time.sleep(1)  # 避免过度消耗CPU

def handle_signal(sig, frame):
    """处理终止信号"""
    global running
    logger.info(f"收到信号 {sig}，准备关闭...")
    running = False
    
    # 关闭线程池
    thread_pool.shutdown(wait=True)
    
    # 关闭连接
    redis_client.close()
    
    logger.info("工作进程已安全关闭")
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    logger.info("知识库工作进程启动")
    
    # 启动任务轮询
    poll_thread = threading.Thread(target=poll_tasks)
    poll_thread.daemon = True
    poll_thread.start()
    
    # 主线程保持运行
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_signal(signal.SIGINT, None)

if __name__ == "__main__":
    main()
