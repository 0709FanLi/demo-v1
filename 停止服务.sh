#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}   停止 AI-RAG 服务${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. 停止前端
echo -e "${YELLOW}[1/3] 停止前端服务...${NC}"
pkill -f "react-scripts start" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 前端已停止${NC}"
else
    echo -e "${YELLOW}  前端未运行${NC}"
fi

# 2. 停止后端
echo -e "${YELLOW}[2/3] 停止后端服务...${NC}"
pkill -f "uvicorn src.main:app" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 后端已停止${NC}"
else
    echo -e "${YELLOW}  后端未运行${NC}"
fi

# 3. 停止 Milvus（可选）
echo -e "${YELLOW}[3/3] 停止 Milvus 服务...${NC}"
read -p "是否停止 Milvus？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$PROJECT_ROOT"
    docker compose -f docker-compose-milvus.yml stop
    echo -e "${GREEN}✓ Milvus 已停止${NC}"
else
    echo -e "${YELLOW}  保持 Milvus 运行${NC}"
fi

echo ""
echo -e "${GREEN}✓ 服务停止完成${NC}"
echo ""

