 #!/bin/bash

# 高性能本地知识库系统启动脚本
echo "DeepSeek本地知识库系统启动脚本"
echo "================================"

# 检查Docker状态
echo "检查Docker服务..."
if ! systemctl is-active --quiet docker; then
    echo "Docker服务未运行，正在启动..."
    sudo systemctl start docker
fi

# 检查NVIDIA GPU状态
if command -v nvidia-smi &> /dev/null; then
    echo "检查GPU状态:"
    nvidia-smi | head -n 10
else
    echo "警告: 未检测到NVIDIA GPU。系统性能可能受到影响。"
fi

# 启动服务
echo "启动所有服务..."
docker-compose up -d

# 等待服务就绪
echo "等待服务就绪..."
sleep 10

# 检查服务状态
echo "检查服务状态:"
docker-compose ps

# 检查Ollama模型
echo "检查DeepSeek模型状态..."
docker exec -it knowledge-base-system_ollama_1 ollama list

# 显示访问信息
echo "================================"
echo "系统已启动!"
echo "- API服务: http://localhost:8000"
echo "- 前端界面: http://localhost:8501"
echo "- Qdrant管理界面: http://localhost:6333/dashboard"
echo "================================"
echo "使用以下命令查看日志:"
echo "docker-compose logs -f"
echo "使用以下命令停止服务:"
echo "docker-compose down"
echo "================================"

