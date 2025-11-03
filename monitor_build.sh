#!/bin/bash

#########################################
# 构建监控脚本 - 自动检查构建完成状态
# 用途：定期检查构建进度，完成后通知
#########################################

SERVER_IP="106.14.204.36"
SERVER_USER="root"
SERVER_PASSWORD="Yuan0730zhen."
SERVER_PORT="22"

CHECK_INTERVAL=60  # 每60秒检查一次
MAX_CHECKS=120     # 最多检查120次（2小时）

echo "开始监控构建进度..."
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo "按 Ctrl+C 可随时停止"
echo ""

CHECK_COUNT=0

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    
    # 检查构建进程是否还在运行
    BUILD_PID=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "ps aux | grep build_in_background.sh | grep -v grep | awk '{print \$2}'" 2>/dev/null)
    
    if [ -z "$BUILD_PID" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⚠️  构建进程已结束，检查构建结果..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # 检查构建日志最后几行
        LAST_LOG=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "tail -10 /root/anti-aging-system/build.log 2>/dev/null")
        
        if echo "$LAST_LOG" | grep -q "部署完成\|✓ 服务启动完成\|Successfully"; then
            echo ""
            echo "✅✅✅ 构建成功完成！✅✅✅"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "📋 服务状态"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "cd /root/anti-aging-system && docker-compose -f docker-compose.prod.yml ps"
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "🌐 访问地址"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "前端: http://$SERVER_IP"
            echo "API文档: http://$SERVER_IP/api/docs"
            echo ""
            
            # 发送系统通知（macOS）
            if command -v osascript &> /dev/null; then
                osascript -e "display notification \"构建完成！服务已启动\" with title \"部署成功\""
            fi
            
            exit 0
        elif echo "$LAST_LOG" | grep -q "ERROR\|构建失败\|failed"; then
            echo ""
            echo "❌❌❌ 构建失败！❌❌❌"
            echo ""
            echo "最后10行日志："
            echo "$LAST_LOG"
            echo ""
            echo "请检查日志: ssh root@$SERVER_IP 'tail -50 /root/anti-aging-system/build.log'"
            exit 1
        else
            echo "构建状态未知，最后日志："
            echo "$LAST_LOG"
            echo ""
            echo "请手动检查: bash check_build_status.sh"
            exit 2
        fi
    else
        # 构建还在进行中
        RUNTIME=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "ps -p $BUILD_PID -o etime= | tr -d ' '" 2>/dev/null)
        LAST_LINE=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "tail -1 /root/anti-aging-system/build.log 2>/dev/null | head -c 100")
        
        printf "\r[检查 #%d] 构建进行中 (运行时间: %s) - %s" "$CHECK_COUNT" "$RUNTIME" "$LAST_LINE"
        
        sleep $CHECK_INTERVAL
    fi
done

echo ""
echo "⚠️  已达到最大检查次数，请手动检查构建状态"
echo "运行: bash check_build_status.sh"

