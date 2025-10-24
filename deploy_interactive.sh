#!/bin/bash

#########################################
# 抗衰老专家咨询系统 - 交互式部署脚本
# 用途：从本地部署到服务器（支持密码输入）
#########################################

set -e

# ========== 配置变量 ==========
SERVER_IP="106.14.204.36"
SERVER_USER="root"
SERVER_PORT="22"
REMOTE_DIR="/root/anti-aging-system"
PROJECT_NAME="抗衰老专家咨询系统"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ========== 函数定义 ==========

print_header() {
    echo -e "${BLUE}"
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 检查必要的命令
check_requirements() {
    print_header "检查部署环境"
    
    if ! command -v rsync &> /dev/null; then
        print_error "缺少 rsync 工具"
        print_info "请安装: brew install rsync"
        exit 1
    fi
    
    if ! command -v ssh &> /dev/null; then
        print_error "缺少 ssh 工具"
        exit 1
    fi
    
    print_success "环境检查完成"
}

# 连接测试
test_connection() {
    print_header "测试服务器连接"
    
    print_info "尝试连接到 $SERVER_IP..."
    print_info "密码: Yuan0730zhen."
    
    if ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -p $SERVER_PORT $SERVER_USER@$SERVER_IP "echo 'Connection OK'" 2>/dev/null; then
        print_success "服务器连接成功"
        return 0
    else
        print_warning "连接测试失败，请确保："
        print_info "1. 服务器 IP 正确: $SERVER_IP"
        print_info "2. SSH 端口开放: $SERVER_PORT"
        print_info "3. 密码正确: Yuan0730zhen."
        read -p "继续部署? (y/N): " continue
        if [[ ! $continue =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 同步代码到服务器
sync_code() {
    print_header "同步代码到服务器"
    
    print_info "准备同步文件..."
    print_warning "可能需要输入服务器密码: Yuan0730zhen."
    
    rsync -avz --delete --progress \
        --exclude 'node_modules/' \
        --exclude 'venv/' \
        --exclude '__pycache__/' \
        --exclude '*.pyc' \
        --exclude '.git/' \
        --exclude 'volumes/' \
        --exclude 'logs/' \
        --exclude '.DS_Store' \
        -e "ssh -p $SERVER_PORT -o StrictHostKeyChecking=no" \
        ./ $SERVER_USER@$SERVER_IP:$REMOTE_DIR/
    
    print_success "代码同步完成"
}

# 在服务器上部署
deploy_on_server() {
    print_header "在服务器上部署应用"
    
    print_info "创建并执行部署脚本..."
    print_warning "可能需要多次输入密码"
    
    # 创建远程部署脚本
    ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "cat > $REMOTE_DIR/deploy_server.sh << 'DEPLOY_EOF'
#!/bin/bash
set -e

cd $REMOTE_DIR

echo '========== 检查 Docker =========='
if ! command -v docker &> /dev/null; then
    echo '安装 Docker...'
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    echo '✓ Docker 安装完成'
else
    echo '✓ Docker 已安装'
    docker --version
fi

echo ''
echo '========== 检查 Docker Compose =========='
if ! command -v docker-compose &> /dev/null; then
    echo '安装 Docker Compose...'
    curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo '✓ Docker Compose 安装完成'
else
    echo '✓ Docker Compose 已安装'
    docker-compose --version
fi

echo ''
echo '========== 配置环境变量 =========='
if [ ! -f .env ]; then
    cp env.production.template .env
    echo '✓ 环境变量文件已创建'
else
    echo '✓ 环境变量文件已存在'
fi

echo ''
echo '========== 创建必要目录 =========='
mkdir -p logs/backend logs/nginx volumes/etcd volumes/minio volumes/milvus backend/data
chmod -R 755 volumes/ logs/
echo '✓ 目录创建完成'

echo ''
echo '========== 停止旧容器 =========='
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
sleep 2

echo ''
echo '========== 构建并启动服务 =========='
echo '这可能需要几分钟，请耐心等待...'
docker-compose -f docker-compose.prod.yml up -d --build

echo ''
echo '========== 等待服务启动 =========='
echo '等待30秒...'
sleep 30

echo ''
echo '========== 检查服务状态 =========='
docker-compose -f docker-compose.prod.yml ps

echo ''
echo '========== 配置防火墙 =========='
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp 2>/dev/null || true
    ufw allow 443/tcp 2>/dev/null || true
    ufw allow 22/tcp 2>/dev/null || true
    echo '✓ 防火墙规则已添加'
else
    echo 'ℹ 未检测到 ufw，跳过防火墙配置'
fi

echo ''
echo '=========================================='
echo '✓ 部署完成！'
echo '=========================================='
echo ''
echo '访问地址：'
echo '  前端: http://106.14.204.36'
echo '  API: http://106.14.204.36/api/docs'
echo ''
echo '查看日志:'
echo '  docker-compose -f docker-compose.prod.yml logs -f'
echo ''
echo '重启服务:'
echo '  docker-compose -f docker-compose.prod.yml restart'
echo ''
DEPLOY_EOF
"

    print_info "执行部署脚本..."
    ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "chmod +x $REMOTE_DIR/deploy_server.sh && $REMOTE_DIR/deploy_server.sh"
    
    print_success "服务器部署完成"
}

# 健康检查
health_check() {
    print_header "服务健康检查"
    
    print_info "等待服务完全启动..."
    sleep 15
    
    print_info "检查前端服务..."
    if curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://$SERVER_IP 2>/dev/null | grep -q "200"; then
        print_success "前端服务正常"
    else
        print_warning "前端服务可能未就绪，请稍后访问"
    fi
    
    print_info "检查后端服务..."
    if curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://$SERVER_IP/api/health 2>/dev/null | grep -q "200"; then
        print_success "后端服务正常"
    else
        print_warning "后端服务可能未就绪，请稍后访问"
    fi
}

# 显示部署信息
show_info() {
    print_header "部署完成"
    
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════╗"
    echo "║  $PROJECT_NAME 部署成功！        ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "访问信息："
    echo "  🌐 前端应用: http://$SERVER_IP"
    echo "  📡 API文档:  http://$SERVER_IP/api/docs"
    echo "  ❤️  健康检查: http://$SERVER_IP/api/health"
    echo ""
    echo "管理命令（在服务器上执行）："
    echo "  # SSH 登录"
    echo "  ssh $SERVER_USER@$SERVER_IP"
    echo ""
    echo "  # 查看服务状态"
    echo "  cd $REMOTE_DIR && docker-compose -f docker-compose.prod.yml ps"
    echo ""
    echo "  # 查看日志"
    echo "  cd $REMOTE_DIR && docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    echo "  # 重启服务"
    echo "  cd $REMOTE_DIR && docker-compose -f docker-compose.prod.yml restart"
    echo ""
    echo "  # 停止服务"
    echo "  cd $REMOTE_DIR && docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "  # 备份数据"
    echo "  cd $REMOTE_DIR && bash backup.sh"
    echo ""
    echo -e "${NC}"
    
    print_info "提示: 如果服务未就绪，请等待几分钟后再访问"
}

# ========== 主流程 ==========
main() {
    clear
    
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║  $PROJECT_NAME - 交互式部署        ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${YELLOW}注意：部署过程中可能需要多次输入服务器密码${NC}"
    echo -e "${YELLOW}密码: Yuan0730zhen.${NC}"
    echo ""
    
    # 确认部署
    read -p "确认开始部署到 $SERVER_IP? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_info "部署已取消"
        exit 0
    fi
    
    echo ""
    
    # 执行部署流程
    check_requirements
    test_connection
    sync_code
    deploy_on_server
    health_check
    show_info
    
    print_success "🎉 部署流程完成！"
}

# 运行主流程
main

