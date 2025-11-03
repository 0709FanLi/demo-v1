#!/bin/bash

#########################################
# 构建状态检查脚本
# 用途：快速查看服务器上的构建进度
#########################################

SERVER_IP="106.14.204.36"
SERVER_USER="root"
SERVER_PASSWORD="Yuan0730zhen."
SERVER_PORT="22"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          检查服务器构建状态                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# 检查构建进程
BUILD_PID=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "ps aux | grep build_in_background.sh | grep -v grep | awk '{print \$2}'" 2>/dev/null)

if [ -n "$BUILD_PID" ]; then
    echo -e "${GREEN}✓ 构建进程: 运行中 (PID: $BUILD_PID)${NC}"
    RUNTIME=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "ps -p $BUILD_PID -o etime= | tr -d ' '" 2>/dev/null)
    echo "  运行时间: $RUNTIME"
else
    echo -e "${YELLOW}✗ 构建进程: 未运行${NC}"
    echo ""
    echo "检查构建结果..."
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "tail -20 /root/anti-aging-system/build.log 2>/dev/null | tail -10"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 构建日志统计"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

LOG_INFO=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "wc -l /root/anti-aging-system/build.log 2>/dev/null | awk '{print \$1}' && du -h /root/anti-aging-system/build.log 2>/dev/null | awk '{print \$1}'")
LINES=$(echo "$LOG_INFO" | head -1)
SIZE=$(echo "$LOG_INFO" | tail -1)

echo "日志行数: $LINES"
echo "日志大小: $SIZE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 当前构建步骤 (最后5行关键信息)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "tail -50 /root/anti-aging-system/build.log 2>/dev/null | grep -E '(Downloading|Installing|Collecting|Building|✓|✗|ERROR|Successfully|完成)' | tail -5"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 最新日志 (最后3行)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "tail -3 /root/anti-aging-system/build.log 2>/dev/null"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 Docker 容器状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "cd /root/anti-aging-system && docker-compose -f docker-compose.prod.yml ps 2>/dev/null || echo '容器未启动'"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}💡 提示${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "实时查看日志: ssh root@$SERVER_IP 'tail -f /root/anti-aging-system/build.log'"
echo "查看完整状态: ssh root@$SERVER_IP 'bash /root/anti-aging-system/build_status.sh'"
echo ""

