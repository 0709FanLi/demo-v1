#!/bin/bash

#########################################
# 抗衰老专家咨询系统 - 全自动部署脚本
# 用途：从本地自动部署到服务器（无需交互）
#########################################

set -e  # 遇到错误立即退出

# ========== 配置变量 ==========
SERVER_IP="106.14.204.36"
SERVER_USER="root"
SERVER_PASSWORD="Yuan0730zhen."
SERVER_PORT="22"
REMOTE_DIR="/root/anti-aging-system"
PROJECT_NAME="抗衰老专家咨询系统"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    print_header "1/6 检查部署环境"
    
    local missing_tools=()
    
    if ! command -v rsync &> /dev/null; then
        missing_tools+=("rsync")
    fi
    
    if ! command -v sshpass &> /dev/null; then
        print_error "未安装 sshpass"
        print_info "请先安装: brew install hudochenkov/sshpass/sshpass"
        exit 1
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_error "缺少必要工具: ${missing_tools[*]}"
        print_info "请安装: brew install ${missing_tools[*]}"
        exit 1
    fi
    
    print_success "环境检查完成"
    echo ""
}

# 连接测试
test_connection() {
    print_header "2/6 测试服务器连接"
    
    if sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -p $SERVER_PORT $SERVER_USER@$SERVER_IP "echo 'OK'" &> /dev/null; then
        print_success "服务器连接成功 ($SERVER_IP)"
    else
        print_error "无法连接到服务器 $SERVER_IP"
        print_info "请检查网络、IP地址和密码"
        exit 1
    fi
    echo ""
}

# 构建前端
build_frontend() {
    print_header "3/7 构建前端应用"
    
    print_info "检查前端依赖..."
    if [ ! -d "frontend/node_modules" ]; then
        print_info "安装前端依赖..."
        cd frontend && npm install && cd ..
    fi
    
    print_info "构建前端生产版本..."
    cd frontend
    if npm run build; then
        print_success "前端构建成功"
    else
        print_error "前端构建失败"
        exit 1
    fi
    cd ..
    echo ""
}

# 同步代码到服务器
sync_code() {
    print_header "4/7 同步代码到服务器"
    
    print_info "开始同步文件..."
    
    # 使用 rsync 同步（排除不需要的文件，但包含 build 目录）
    sshpass -p "$SERVER_PASSWORD" rsync -avz --delete \
        --exclude 'node_modules/' \
        --exclude 'venv/' \
        --exclude '__pycache__/' \
        --exclude '*.pyc' \
        --exclude '.git/' \
        --exclude 'volumes/' \
        --exclude 'logs/' \
        --exclude '.DS_Store' \
        -e "ssh -p $SERVER_PORT -o StrictHostKeyChecking=no" \
        ./ $SERVER_USER@$SERVER_IP:$REMOTE_DIR/ \
        2>&1 | tail -n 10
    
    print_success "代码同步完成（包含前端构建产物）"
    echo ""
}

# 执行远程命令
exec_remote() {
    local cmd=$1
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no -p $SERVER_PORT $SERVER_USER@$SERVER_IP "$cmd"
}

# 在服务器上部署
deploy_on_server() {
    print_header "5/7 在服务器上部署应用"
    
    print_info "创建部署脚本..."
    
    # 创建远程部署脚本
    exec_remote "cat > $REMOTE_DIR/deploy_server.sh << 'EOF'
#!/bin/bash
set -e

cd $REMOTE_DIR

echo '========== 检查 Docker =========='
if ! command -v docker &> /dev/null; then
    echo '正在安装 Docker...'
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    echo '✓ Docker 安装完成'
else
    echo '✓ Docker 已安装'
fi

echo ''
echo '========== 检查 Docker Compose =========='
if ! command -v docker-compose &> /dev/null; then
    echo '正在安装 Docker Compose...'
    curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo '✓ Docker Compose 安装完成'
else
    echo '✓ Docker Compose 已安装'
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
echo '✓ 目录创建完成'

echo ''
echo '========== 停止旧容器 =========='
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

echo ''
echo '========== 构建并启动服务 =========='
echo '注意：前端使用本地构建产物（Dockerfile.simple），后端和基础设施服务将重新构建'
echo '正在构建镜像，这可能需要几分钟...'
docker-compose -f docker-compose.prod.yml up -d --build

echo ''
echo '========== 等待服务启动 =========='
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
    echo '✓ 防火墙配置完成'
fi

echo ''
echo '✓ 部署完成！'
EOF
"

    print_info "执行部署..."
    exec_remote "chmod +x $REMOTE_DIR/deploy_server.sh && $REMOTE_DIR/deploy_server.sh"
    
    print_success "服务器部署完成"
    echo ""
}

# 健康检查
health_check() {
    print_header "6/7 服务健康检查"
    
    print_info "等待服务完全启动..."
    sleep 10
    
    # 检查前端
    print_info "检查前端服务..."
    if curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://$SERVER_IP 2>/dev/null | grep -q "200"; then
        print_success "前端服务正常"
    else
        print_warning "前端服务可能未就绪（请稍后访问）"
    fi
    
    # 检查后端
    print_info "检查后端API..."
    if curl -s -o /dev/null -w "%{http_code}" --max-time 10 http://$SERVER_IP/api/health 2>/dev/null | grep -q "200"; then
        print_success "后端服务正常"
    else
        print_warning "后端服务可能未就绪（请稍后访问）"
    fi
    echo ""
}

# 显示部署信息
show_info() {
    print_header "7/7 部署完成"
    
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════╗"
    echo "║    $PROJECT_NAME 部署成功！      ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${GREEN}访问地址：${NC}"
    echo "  🌐 前端应用: ${BLUE}http://$SERVER_IP${NC}"
    echo "  📡 API文档:  ${BLUE}http://$SERVER_IP/api/docs${NC}"
    echo "  ❤️  健康检查: ${BLUE}http://$SERVER_IP/api/health${NC}"
    echo ""
    echo -e "${YELLOW}管理命令（SSH到服务器后执行）：${NC}"
    echo "  查看日志: cd $REMOTE_DIR && docker-compose -f docker-compose.prod.yml logs -f"
    echo "  重启服务: cd $REMOTE_DIR && docker-compose -f docker-compose.prod.yml restart"
    echo "  停止服务: cd $REMOTE_DIR && docker-compose -f docker-compose.prod.yml down"
    echo "  备份数据: cd $REMOTE_DIR && bash backup.sh"
    echo ""
}

# ========== 主流程 ==========
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║  $PROJECT_NAME - 全自动部署        ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${GREEN}目标服务器: $SERVER_IP${NC}"
    echo -e "${GREEN}开始自动部署...${NC}"
    echo ""
    
    # 执行部署流程
    check_requirements
    test_connection
    build_frontend
    sync_code
    deploy_on_server
    health_check
    show_info
    
    echo -e "${GREEN}🎉 部署流程完成！${NC}"
    echo ""
}

# 运行主流程
main

