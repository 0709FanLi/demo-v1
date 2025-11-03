#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}   AI-RAG 服务启动脚本${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 1. 检查并启动 Milvus
echo -e "${YELLOW}[1/3] 检查 Milvus 服务...${NC}"
cd "$PROJECT_ROOT"

if docker compose -f docker-compose-milvus.yml ps | grep -q "milvus-standalone.*Up"; then
    echo -e "${GREEN}✓ Milvus 已运行${NC}"
else
    echo -e "${YELLOW}  启动 Milvus...${NC}"
    docker compose -f docker-compose-milvus.yml up -d
    echo -e "${GREEN}✓ Milvus 启动成功${NC}"
fi

# 等待 Milvus 就绪
echo -e "${YELLOW}  等待 Milvus 就绪...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:9091/healthz -m 2 | grep -q "OK"; then
        echo -e "${GREEN}✓ Milvus 就绪${NC}"
        break
    fi
    sleep 1
done

echo ""

# 2. 启动后端
echo -e "${YELLOW}[2/3] 启动后端服务...${NC}"
cd "$PROJECT_ROOT/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ 虚拟环境不存在，请先运行: python3 -m venv venv${NC}"
    exit 1
fi

# 激活虚拟环境并启动
source venv/bin/activate

# 停止旧进程
pkill -f "uvicorn src.main:app" 2>/dev/null
sleep 2

# 启动新进程
nohup python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 > backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${YELLOW}  等待后端启动...${NC}"
sleep 15

# 验证后端
if curl -s http://localhost:8001/docs -m 3 > /dev/null; then
    echo -e "${GREEN}✓ 后端启动成功 (PID: $BACKEND_PID)${NC}"
else
    echo -e "${RED}✗ 后端启动失败，查看日志: backend/backend.log${NC}"
fi

echo ""

# 3. 启动前端
echo -e "${YELLOW}[3/3] 启动前端服务...${NC}"
cd "$PROJECT_ROOT/frontend"

# 停止旧进程
pkill -f "vite" 2>/dev/null
sleep 2

# 启动新进程（使用 Vite）
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${YELLOW}  等待前端启动...${NC}"
sleep 15

# 验证前端
if curl -s http://localhost:3000 -m 3 > /dev/null; then
    echo -e "${GREEN}✓ 前端启动成功 (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ 前端启动失败，查看日志: frontend/frontend.log${NC}"
fi

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}   ✓ 所有服务启动完成${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${BLUE}📚 访问地址:${NC}"
echo -e "   ${GREEN}前端界面:${NC} http://localhost:3000"
echo -e "   ${GREEN}后端 API:${NC} http://localhost:8001/docs"
echo -e "   ${GREEN}Milvus:${NC}   localhost:19530"
echo ""
echo -e "${BLUE}📝 日志文件:${NC}"
echo -e "   后端: backend/backend.log"
echo -e "   前端: frontend/frontend.log"
echo ""
echo -e "${BLUE}🛑 停止服务:${NC}"
echo -e "   运行: bash 停止服务.sh"
echo ""

