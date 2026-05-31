#!/bin/bash
# ============================================
# 快速更新脚本
# 用途：拉取最新代码并重新部署
# 使用：./scripts/update.sh
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

# 拉取最新代码
pull_latest_code() {
    log_info "拉取最新代码..."
    git pull origin main
    log_info "代码更新完成"
}

# 检查是否有 Dockerfile 变更
check_dockerfile_changes() {
    local changes=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -E "(Dockerfile|docker-compose)" || true)
    
    if [ -n "$changes" ]; then
        log_warn "检测到 Docker 配置变更，需要重新构建"
        return 0
    else
        log_info "无 Docker 配置变更，仅重启服务"
        return 1
    fi
}

# 重新构建并重启
rebuild_and_restart() {
    log_info "重新构建并重启服务..."
    docker compose -f docker-compose.prod.yml up -d --build
}

# 仅重启服务
restart_only() {
    log_info "重启服务..."
    docker compose -f docker-compose.prod.yml restart
}

# 验证更新
verify_update() {
    log_info "验证更新..."
    
    # 检查容器状态
    log_info "容器状态："
    docker compose -f docker-compose.prod.yml ps
    
    # 测试 API
    log_info ""
    log_info "API 测试："
    if curl -s http://localhost:8000/health | grep -q '"status":"ok"'; then
        log_info "✓ 后端健康检查通过"
    else
        log_warn "✗ 后端健康检查失败"
    fi
}

# 主函数
main() {
    log_info "=========================================="
    log_info "开始更新"
    log_info "=========================================="
    
    check_project_root
    pull_latest_code
    
    if check_dockerfile_changes; then
        rebuild_and_restart
    else
        restart_only
    fi
    
    verify_update
    
    log_info ""
    log_info "=========================================="
    log_info "更新完成！"
    log_info "=========================================="
}

main "$@"
