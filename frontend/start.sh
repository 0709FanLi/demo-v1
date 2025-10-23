#!/bin/bash

# 前端启动脚本

echo "🚀 启动RAG智能对话系统 - 前端..."
echo ""

cd /Users/liguangyuan/Documents/GitHub/demo-v1/frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

echo "✅ 启动React开发服务器..."
echo "🌐 访问地址: http://localhost:3000"
echo ""

npm start

