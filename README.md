# 需求管理 AI 服务

基于 LangChain + Ollama + ChromaDB 的智能需求管理服务。

## 前置条件

1. 宿主机安装并运行 Ollama: `ollama serve`
2. 拉取模型: `ollama pull qwen2.5:7b`
3. 安装 Docker 和 Docker Compose

## 快速启动

```bash
# 构建并启动
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
