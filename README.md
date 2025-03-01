# DeepSeek本地知识库系统

一个高性能的本地知识库系统，基于DeepSeek大模型，支持多种文档格式、本地检索、问答和分析功能。

## 系统特性

- **基于DeepSeek模型的本地部署**：无需外部API，保护数据隐私
- **多格式文档处理**：支持PDF、Word、Excel、TXT、HTML等格式
- **高效检索**：支持5000+份文档的语义检索
- **GraphRAG增强**：基于图结构的高效检索与推理
- **多模态交互**：聊天、搜索、分析多种交互方式
- **高性能架构**：基于Redis+Qdrant的高性能存储
- **容器化部署**：基于Docker的简单部署

## 系统要求

- **操作系统**：Ubuntu 20.04 LTS 或更高版本
- **硬件要求**：
  - NVIDIA GPU (推荐RTX 3080+)
  - CUDA 11.7+
  - 内存 16GB+ (推荐32GB+)
  - 存储空间 20GB+
- **软件要求**：
  - Docker 和 Docker Compose
  - NVIDIA Container Toolkit

## 快速开始

### 安装

1. 克隆代码库：
```bash
git clone https://github.com/your-username/knowledge-base-system.git
cd knowledge-base-system
运行安装脚本：

bash scripts/install.sh
启动服务：

bash scripts/start_services.sh
访问系统
前端界面：http://localhost:8501
API文档：http://localhost:8000/docs
使用指南
上传文档
访问前端界面
导航至"文档管理"页面
点击"上传文档"并选择要上传的文件
添加可选的元数据
点击"上传并索引"
聊天问答
导航至"聊天问答"页面
在输入框中输入您的问题
系统将从您的知识库中检索相关信息并生成回答
搜索
导航至"搜索"页面
输入搜索查询
查看匹配的文档片段
数据分析
导航至"数据分析"页面
选择文档或输入文本进行分析
查看生成的分析报告和可视化
项目结构

knowledge-base-system/
├── docker/ - Docker配置文件
├── backend/ - 后端服务
│   ├── api/ - FastAPI应用
│   ├── services/ - 核心服务
│   ├── processors/ - 文档处理器
│   └── embeddings/ - 向量化模块
├── frontend/ - Streamlit前端
├── configs/ - 配置文件
└── scripts/ - 安装和启动脚本
问题排查
常见问题
服务启动失败
检查Docker服务是否运行
检查GPU驱动和CUDA是否正确安装
查看日志：docker-compose logs -f
无法上传文档
检查文件格式是否受支持
检查文件大小是否超过限制
查看API服务日志
模型加载错误
确保DeepSeek模型已正确下载
检查GPU内存是否足够
查看Ollama服务日志
贡献与支持
欢迎提交问题和改进建议，请使用GitHub Issues。

许可证
本项目采用MIT许可证，详情请参见LICENSE文件。
```
