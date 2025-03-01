 #!/bin/bash

# 高性能本地知识库系统安装脚本
echo "DeepSeek本地知识库系统安装脚本"
echo "================================"

# 确认CUDA环境
echo "正在检查CUDA环境..."
if command -v nvidia-smi &> /dev/null; then
    echo "发现NVIDIA GPU:"
    nvidia-smi
else
    echo "警告: 未检测到NVIDIA GPU。此系统需要NVIDIA GPU以获得最佳性能。"
    read -p "是否继续安装? (y/n): " continue_install
    if [[ "$continue_install" != "y" && "$continue_install" != "Y" ]]; then
        echo "安装已取消。"
        exit 1
    fi
fi

# 检查Docker和Docker Compose
echo "检查Docker环境..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo "Docker已安装: $docker_version"
else
    echo "错误: 未安装Docker。请先安装Docker。"
    echo "可参考: https://docs.docker.com/engine/install/ubuntu/"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version)
    echo "Docker Compose已安装: $compose_version"
else
    echo "错误: 未安装Docker Compose。请先安装Docker Compose。"
    echo "可参考: https://docs.docker.com/compose/install/"
    exit 1
fi

# 创建必要的目录
echo "创建项目目录..."
mkdir -p data/uploads
mkdir -p data/models
mkdir -p logs

# 设置权限
echo "设置目录权限..."
chmod -R 755 data
chmod -R 755 logs

# 确认Ollama GPU访问
echo "配置Ollama GPU访问..."
if command -v nvidia-smi &> /dev/null; then
    echo "确保nvidia-container-toolkit已安装"
    if ! command -v nvidia-container-toolkit &> /dev/null; then
        echo "安装nvidia-container-toolkit..."
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
        curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
        curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
        sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
        sudo systemctl restart docker
    fi
fi

# 拉取必要的Docker镜像
echo "拉取必要的Docker镜像..."
docker pull redis:6.2
docker pull qdrant/qdrant:latest
docker pull ollama/ollama:latest

# 构建自定义镜像
echo "构建项目Docker镜像..."
docker-compose build

# 设置DeepSeek模型
echo "准备下载DeepSeek模型(这可能需要一些时间)..."
read -p "是否现在下载DeepSeek模型? (y/n): " download_model
if [[ "$download_model" == "y" || "$download_model" == "Y" ]]; then
    echo "启动Ollama服务..."
    docker-compose up -d ollama
    echo "等待Ollama服务启动..."
    sleep 10
    
    echo "下载DeepSeek-V3模型..."
    docker exec -it knowledge-base-system_ollama_1 ollama pull deepseek/deepseek-v3
    
    echo "下载DeepSeek嵌入模型..."
    docker exec -it knowledge-base-system_ollama_1 ollama pull deepseek/deepseek-embeddings
    
    echo "停止临时Ollama服务..."
    docker-compose stop ollama
else
    echo "跳过模型下载。请在系统启动后手动下载模型。"
fi

# 完成安装
echo "安装完成!"
echo "使用以下命令启动系统:"
echo "bash scripts/start_services.sh"
