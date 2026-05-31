#!/bin/bash
# ============================================
# 一键部署脚本
# 用途：构建并启动所有服务
# 使用：./scripts/deploy.sh
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

# 检查是否在项目根目录
check_project_root() {
    if [ ! -f "docker-compose.prod.yml" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
}

# 检查 .env 文件
check_env_file() {
    if [ ! -f ".env" ]; then
        log_error ".env 文件不存在"
        log_info "请先复制并配置 .env 文件："
        log_info "  cp .env.example .env"
        log_info "  vim .env"
        exit 1
    fi
    
    # 检查关键变量
    source .env
    
    if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
        log_error "MYSQL_ROOT_PASSWORD 未设置"
        exit 1
    fi
    
    if [ -z "$MYSQL_PASSWORD" ]; then
        log_error "MYSQL_PASSWORD 未设置"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        log_error "SECRET_KEY 未设置"
        exit 1
    fi
    
    if [ -z "$DOMAIN" ]; then
        log_error "DOMAIN 未设置"
        exit 1
    fi
    
    log_info "环境变量检查通过"
}

# 检查密码安全性
check_password_security() {
    source .env
    
    # 检查密码是否包含特殊字符
    if echo "$MYSQL_ROOT_PASSWORD" | grep -qE '[$!#&]'; then
        log_warn "MYSQL_ROOT_PASSWORD 包含特殊字符，可能导致连接失败"
        log_warn "建议使用纯字母数字密码"
    fi
    
    if echo "$MYSQL_PASSWORD" | grep -qE '[$!#&]'; then
        log_warn "MYSQL_PASSWORD 包含特殊字符，可能导致连接失败"
        log_warn "建议使用纯字母数字密码"
    fi
}

# 拉取最新代码
pull_latest_code() {
    log_info "拉取最新代码..."
    git pull origin main
    log_info "代码更新完成"
}

# 构建并启动服务
build_and_start() {
    log_info "构建并启动服务..."
    docker compose -f docker-compose.prod.yml up -d --build
    log_info "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待数据库
    log_info "等待数据库启动..."
    for i in {1..30}; do
        if docker inspect exam-db-prod --format='{{.State.Health.Status}}' 2>/dev/null | grep -q "healthy"; then
            log_info "数据库已就绪"
            break
        fi
        sleep 2
    done
    
    # 等待后端
    log_info "等待后端启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_info "后端已就绪"
            break
        fi
        sleep 2
    done
    
    # 等待前端
    log_info "等待前端启动..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            log_info "前端已就绪"
            break
        fi
        sleep 2
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
    source .env
    
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
    log_info "常用命令："
    log_info "  查看日志：docker compose -f docker-compose.prod.yml logs -f"
    log_info "  重启服务：docker compose -f docker-compose.prod.yml restart"
    log_info "  停止服务：docker compose -f docker-compose.prod.yml down"
    log_info "  更新部署：./scripts/deploy.sh"
    log_info ""
}

# 主函数
main() {
    log_info "=========================================="
    log_info "开始部署"
    log_info "=========================================="
    
    check_project_root
    check_env_file
    check_password_security
    pull_latest_code
    build_and_start
    wait_for_services
    verify_deployment
    show_deployment_info
}

main "$@"
