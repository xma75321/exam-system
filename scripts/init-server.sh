#!/bin/bash
# ============================================
# 服务器初始化脚本
# 用途：新服务器首次部署前的环境准备
# 使用：curl -sSL https://raw.githubusercontent.com/your-username/exam-system/main/scripts/init-server.sh | bash
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

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 用户运行此脚本"
        exit 1
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    apt update
    apt upgrade -y
}

# 安装 Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker 已安装: $(docker --version)"
    else
        log_info "安装 Docker..."
        apt install -y docker.io
        systemctl enable docker
        systemctl start docker
        log_info "Docker 安装完成: $(docker --version)"
    fi
}

# 安装 Docker Compose
install_docker_compose() {
    if docker compose version &> /dev/null; then
        log_info "Docker Compose 已安装: $(docker compose version --short)"
    else
        log_info "安装 Docker Compose..."
        apt install -y docker-compose-plugin
        log_info "Docker Compose 安装完成: $(docker compose version --short)"
    fi
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    # 安装 ufw
    apt install -y ufw
    
    # 允许 SSH
    ufw allow 22/tcp
    
    # 允许 HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # 启用防火墙
    ufw --force enable
    
    log_info "防火墙配置完成"
}

# 创建应用目录
create_app_dir() {
    log_info "创建应用目录..."
    mkdir -p /opt/app
    log_info "应用目录创建完成: /opt/app"
}

# 安装常用工具
install_tools() {
    log_info "安装常用工具..."
    apt install -y git curl wget vim htop net-tools
}

# 主函数
main() {
    log_info "=========================================="
    log_info "开始初始化服务器"
    log_info "=========================================="
    
    check_root
    update_system
    install_docker
    install_docker_compose
    configure_firewall
    install_tools
    create_app_dir
    
    log_info "=========================================="
    log_info "服务器初始化完成！"
    log_info "=========================================="
    log_info ""
    log_info "下一步："
    log_info "  1. 克隆项目：git clone <repo-url> /opt/app/exam-system"
    log_info "  2. 配置环境：cd /opt/app/exam-system && cp .env.example .env && vim .env"
    log_info "  3. 部署应用：./scripts/deploy.sh"
}

main "$@"
