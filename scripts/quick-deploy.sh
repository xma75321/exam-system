#!/bin/bash
# ============================================
# 一键部署脚本（全新服务器）
# 用途：从零开始部署整个应用
# 使用：curl -sSL https://raw.githubusercontent.com/your-username/exam-system/main/scripts/quick-deploy.sh | bash -s -- --domain=your-domain.com
# ============================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 解析参数
DOMAIN=""
REPO_URL="https://github.com/xma75321/exam-system.git"
APP_DIR="/opt/app/exam-system"

while [[ $# -gt 0 ]]; do
    case $1 in
        --domain=*)
            DOMAIN="${1#*=}"
            shift
            ;;
        --repo=*)
            REPO_URL="${1#*=}"
            shift
            ;;
        --dir=*)
            APP_DIR="${1#*=}"
            shift
            ;;
        *)
            log_error "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查参数
if [ -z "$DOMAIN" ]; then
    log_error "请指定域名或 IP"
    log_info "使用方法: curl -sSL <url> | bash -s -- --domain=your-domain.com"
    exit 1
fi

# 生成随机密码
generate_password() {
    openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 16
}

# 生成随机密钥
generate_secret_key() {
    openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 用户运行此脚本"
        exit 1
    fi
}

# 初始化服务器
init_server() {
    log_info "初始化服务器..."
    
    # 更新系统
    apt update
    apt upgrade -y
    
    # 安装 Docker
    if ! command -v docker &> /dev/null; then
        apt install -y docker.io
        systemctl enable docker
        systemctl start docker
    fi
    
    # 安装 Docker Compose
    if ! docker compose version &> /dev/null; then
        apt install -y docker-compose-plugin
    fi
    
    # 安装常用工具
    apt install -y git curl wget vim htop net-tools ufw
    
    # 配置防火墙
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    
    log_info "服务器初始化完成"
}

# 克隆代码
clone_repo() {
    log_info "克隆代码..."
    
    if [ -d "$APP_DIR" ]; then
        log_warn "目录已存在，拉取最新代码..."
        cd "$APP_DIR"
        git pull origin main
    else
        git clone "$REPO_URL" "$APP_DIR"
        cd "$APP_DIR"
    fi
    
    log_info "代码准备完成"
}

# 配置环境变量
configure_env() {
    log_info "配置环境变量..."
    
    cd "$APP_DIR"
    
    # 生成密码
    MYSQL_ROOT_PASSWORD=$(generate_password)
    MYSQL_PASSWORD=$(generate_password)
    SECRET_KEY=$(generate_secret_key)
    
    # 创建 .env 文件
    cat > .env << EOF
# 数据库配置
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
MYSQL_USER=exam_user
MYSQL_PASSWORD=${MYSQL_PASSWORD}
MYSQL_DATABASE=exam_system

# 应用配置
SECRET_KEY=${SECRET_KEY}
DOMAIN=${DOMAIN}

# CORS 配置（自动生成）
CORS_ORIGINS=["http://${DOMAIN}","http://localhost:3000"]
EOF
    
    log_info "环境变量配置完成"
    log_info "MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}"
    log_info "MYSQL_PASSWORD: ${MYSQL_PASSWORD}"
    log_info "SECRET_KEY: ${SECRET_KEY}"
    
    # 保存密码到文件
    cat > /root/exam-system-credentials.txt << EOF
==========================================
考试系统部署信息
==========================================
域名: ${DOMAIN}
数据库 Root 密码: ${MYSQL_ROOT_PASSWORD}
数据库用户密码: ${MYSQL_PASSWORD}
应用密钥: ${SECRET_KEY}
==========================================
EOF
    
    log_info "密码已保存到 /root/exam-system-credentials.txt"
}

# 部署应用
deploy_app() {
    log_info "部署应用..."
    
    cd "$APP_DIR"
    
    # 构建并启动服务
    docker compose -f docker-compose.prod.yml up -d --build
    
    log_info "应用部署完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待数据库
    log_info "等待数据库启动..."
    for i in {1..60}; do
        if docker inspect exam-db-prod --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
            log_info "数据库已就绪"
            break
        fi
        sleep 3
    done
    
    # 等待后端
    log_info "等待后端启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_info "后端已就绪"
            break
        fi
        sleep 3
    done
    
    # 等待前端
    log_info "等待前端启动..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            log_info "前端已就绪"
            break
        fi
        sleep 3
    done
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    # 检查容器状态
    log_info "容器状态："
    docker compose -f docker-compose.prod.yml ps
    
    # 检查健康状态
    log_info ""
    log_info "健康检查："
    docker inspect exam-db-prod --format='数据库: {{.State.Health.Status}}' 2>/dev/null || log_warn "数据库容器未找到"
    docker inspect exam-backend-prod --format='后端: {{.State.Health.Status}}' 2>/dev/null || log_warn "后端容器未找到"
    docker inspect exam-frontend-prod --format='前端: {{.State.Health.Status}}' 2>/dev/null || log_warn "前端容器未找到"
    
    # 测试 API
    log_info ""
    log_info "API 测试："
    if curl -s http://localhost:8000/health | grep -q '"status":"ok"'; then
        log_info "✓ 后端健康检查通过"
    else
        log_warn "✗ 后端健康检查失败"
    fi
    
    # 测试前端环境变量
    log_info ""
    log_info "前端环境变量："
    docker exec exam-frontend-prod printenv NEXT_PUBLIC_API_URL 2>/dev/null || log_warn "无法获取前端环境变量"
}

# 显示部署信息
show_deployment_info() {
    log_info ""
    log_info "=========================================="
    log_info "部署完成！"
    log_info "=========================================="
    log_info ""
    log_info "访问地址："
    log_info "  http://${DOMAIN}"
    log_info ""
    log_info "API 地址："
    log_info "  http://${DOMAIN}/api"
    log_info ""
    log_info "部署信息已保存到："
    log_info "  /root/exam-system-credentials.txt"
    log_info ""
    log_info "常用命令："
    log_info "  查看日志：cd ${APP_DIR} && docker compose -f docker-compose.prod.yml logs -f"
    log_info "  重启服务：cd ${APP_DIR} && docker compose -f docker-compose.prod.yml restart"
    log_info "  停止服务：cd ${APP_DIR} && docker compose -f docker-compose.prod.yml down"
    log_info "  更新部署：cd ${APP_DIR} && ./scripts/update.sh"
    log_info ""
}

# 主函数
main() {
    log_info "=========================================="
    log_info "开始一键部署"
    log_info "域名: ${DOMAIN}"
    log_info "=========================================="
    
    check_root
    init_server
    clone_repo
    configure_env
    deploy_app
    wait_for_services
    verify_deployment
    show_deployment_info
}

main "$@"
