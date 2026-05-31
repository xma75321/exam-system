#!/bin/bash
set -e

echo "=========================================="
echo "Backend 启动脚本"
echo "=========================================="

# 等待数据库就绪
echo "[1/3] 等待数据库就绪..."
max_retries=30
retry_count=0

while ! python -c "
import pymysql
import os
import sys

try:
    url = os.environ.get('DATABASE_URL', '')
    # 解析数据库连接信息
    parts = url.replace('mysql+pymysql://', '').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')
    host_port = host_db[0].split(':')
    
    conn = pymysql.connect(
        host=host_port[0],
        port=int(host_port[1]) if len(host_port) > 1 else 3306,
        user=user_pass[0],
        password=user_pass[1],
        database=host_db[1]
    )
    conn.close()
    print('数据库连接成功')
    sys.exit(0)
except Exception as e:
    print(f'等待数据库: {e}')
    sys.exit(1)
" 2>/dev/null; then
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        echo "错误: 数据库连接超时"
        exit 1
    fi
    echo "  重试 $retry_count/$max_retries..."
    sleep 2
done

# 执行数据库迁移
echo "[2/3] 执行数据库迁移..."
alembic upgrade head
echo "  数据库迁移完成"

# 启动应用
echo "[3/3] 启动 FastAPI 应用..."
echo "=========================================="

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
