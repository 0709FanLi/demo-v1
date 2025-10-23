#!/bin/bash

# 快速启动脚本 - Python 3.11.7 + 虚拟环境

echo "🚀 启动RAG智能对话系统..."
echo ""

cd /Users/liguangyuan/Documents/GitHub/demo-v1/backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: ./最终解决方案.sh"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境 (Python 3.11.7)..."
source venv/bin/activate

# 显示Python版本
echo "📌 Python版本: $(python --version)"
echo ""

# 检查核心依赖
echo "🔍 检查依赖..."
python -c "import fastapi, uvicorn, dashscope, chromadb" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ 依赖未安装，请先运行: ./最终解决方案.sh"
    exit 1
fi
echo "✅ 依赖检查通过"
echo ""

# 创建数据目录
mkdir -p data/chroma_db

# 启动服务
echo "🚀 启动FastAPI服务..."
echo "📝 API文档: http://localhost:8000/docs"
echo "🔍 健康检查: http://localhost:8000/health"
echo ""
echo "⚠️  按 Ctrl+C 停止服务"
echo ""

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

