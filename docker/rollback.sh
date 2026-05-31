#!/bin/bash
# ============================================
# 生产环境回滚脚本
# ============================================
# 使用方法:
#   ./rollback.sh code <commit_hash>   - 回滚代码到指定版本
#   ./rollback.sh db <revision>         - 回滚数据库到指定版本
#   ./rollback.sh full <commit_hash> <revision> - 完整回滚
#   ./rollback.sh list                  - 列出可用版本
# ============================================

set -e

APP_DIR="/opt/app/exam-system"
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="$APP_DIR/backups"

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

# 显示帮助
show_help() {
    echo "用法: $0 <command> [args]"
    echo ""
    echo "命令:"
    echo "  code <commit_hash>           回滚代码到指定版本"
    echo "  db <revision>                回滚数据库到指定版本"
    echo "  full <commit_hash> <revision> 完整回滚"
    echo "  list                         列出可用版本"
    echo "  backup                       手动备份数据库"
    echo "  status                       显示当前状态"
}

# 列出可用版本
list_versions() {
    echo "=========================================="
    echo "可用的 Git 版本:"
    echo "=========================================="
    cd "$APP_DIR"
    git log --oneline -20
    
    echo ""
    echo "=========================================="
    echo "可用的数据库迁移版本:"
    echo "=========================================="
    docker compose -f "$COMPOSE_FILE" exec -T backend alembic history
    
    echo ""
    echo "=========================================="
    echo "可用的数据库备份:"
    echo "=========================================="
    ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "无备份文件"
}

# 显示当前状态
show_status() {
    echo "=========================================="
    echo "当前状态"
    echo "=========================================="
    
    cd "$APP_DIR"
    
    echo ""
    echo "Git 版本:"
    git log --oneline -1
    
    echo ""
    echo "数据库迁移版本:"
    docker compose -f "$COMPOSE_FILE" exec -T backend alembic current
    
    echo ""
    echo "Docker 容器状态:"
    docker compose -f "$COMPOSE_FILE" ps
}

# 备份数据库
backup_database() {
    log_info "开始备份数据库..."
    
    mkdir -p "$BACKUP_DIR"
    
    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    cd "$APP_DIR"
    docker compose -f "$COMPOSE_FILE" exec -T db mysqldump \
        -u root \
        -p"$MYSQL_ROOT_PASSWORD" \
        exam_system > "$BACKUP_FILE"
    
    gzip "$BACKUP_FILE"
    
    log_info "数据库备份完成: ${BACKUP_FILE}.gz"
}

# 回滚代码
rollback_code() {
    local commit_hash=$1
    
    if [ -z "$commit_hash" ]; then
        log_error "请指定 commit hash"
        exit 1
    fi
    
    log_info "回滚代码到: $commit_hash"
    
    cd "$APP_DIR"
    
    # 检查 commit 是否存在
    if ! git cat-file -e "$commit_hash" 2>/dev/null; then
        log_error "Commit $commit_hash 不存在"
        exit 1
    fi
    
    # 回滚代码
    git checkout "$commit_hash"
    
    # 重新构建镜像
    log_info "重新构建 Docker 镜像..."
    docker compose -f "$COMPOSE_FILE" build --no-cache
    
    # 重启服务
    log_info "重启服务..."
    docker compose -f "$COMPOSE_FILE" up -d
    
    log_info "代码回滚完成"
}

# 回滚数据库
rollback_database() {
    local revision=$1
    
    if [ -z "$revision" ]; then
        log_error "请指定迁移版本"
        exit 1
    fi
    
    log_warn "数据库回滚可能导致数据丢失!"
    read -p "确认继续? (y/N): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "已取消"
        exit 0
    fi
    
    log_info "回滚数据库到: $revision"
    
    cd "$APP_DIR"
    docker compose -f "$COMPOSE_FILE" exec -T backend alembic downgrade "$revision"
    
    log_info "数据库回滚完成"
}

# 完整回滚
full_rollback() {
    local commit_hash=$1
    local revision=$2
    
    if [ -z "$commit_hash" ] || [ -z "$revision" ]; then
        log_error "请指定 commit hash 和迁移版本"
        exit 1
    fi
    
    log_warn "完整回滚将同时回滚代码和数据库!"
    read -p "确认继续? (y/N): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "已取消"
        exit 0
    fi
    
    # 先备份
    backup_database
    
    # 回滚代码
    rollback_code "$commit_hash"
    
    # 回滚数据库
    rollback_database "$revision"
    
    log_info "完整回滚完成"
}

# 主函数
main() {
    local command=$1
    shift
    
    case "$command" in
        list)
            list_versions
            ;;
        status)
            show_status
            ;;
        backup)
            backup_database
            ;;
        code)
            rollback_code "$@"
            ;;
        db)
            rollback_database "$@"
            ;;
        full)
            full_rollback "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
