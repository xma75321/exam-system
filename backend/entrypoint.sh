#!/bin/bash
set -e

echo "=========================================="
echo "Backend startup script"
echo "=========================================="

# Wait for database
echo "[1/3] Waiting for database..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if python -c "
import pymysql, os, sys
try:
    url = os.environ.get('DATABASE_URL', '')
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
    print('Database connected')
    sys.exit(0)
except Exception as e:
    print(f'Waiting: {e}')
    sys.exit(1)
" 2>/dev/null; then
        echo "  Database is ready!"
        break
    fi
    
    retry_count=$((retry_count + 1))
    echo "  Retry $retry_count/$max_retries..."
    sleep 2
done

if [ $retry_count -ge $max_retries ]; then
    echo "ERROR: Database connection timeout"
    exit 1
fi

# Run migrations
echo "[2/3] Running database migrations..."
alembic upgrade head
echo "  Migrations complete"

# Start application
echo "[3/3] Starting FastAPI application..."
echo "=========================================="

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
