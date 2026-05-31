# CI/CD 自动部署完整指南

## 目录

1. [架构概述](#架构概述)
2. [GitHub Secrets 配置](#github-secrets-配置)
3. [服务器初始化](#服务器初始化)
4. [GitHub Actions 配置](#github-actions-配置)
5. [Docker Compose 配置](#docker-compose-配置)
6. [环境变量配置](#环境变量配置)
7. [数据库迁移配置](#数据库迁移配置)
8. [回滚方案](#回滚方案)
9. [运维建议](#运维建议)

---

## 架构概述

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub 仓库                              │
├─────────────────────────────────────────────────────────────────┤
│  develop 分支  ──push──▶  deploy-dev.yml  ──▶  测试环境部署      │
│  main 分支     ──push──▶  deploy-prod.yml ──▶  生产环境部署      │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ubuntu 生产服务器 (45.32.17.107)              │
├─────────────────────────────────────────────────────────────────┤
│  /opt/app/                                                      │
│  ├── exam-system/          # Git 仓库                           │
│  ├── scripts/              # 运维脚本                           │
│  │   ├── deploy.sh         # 快速部署                           │
│  │   └── rollback.sh       # 回滚脚本                           │
│  └── backups/              # 数据库备份                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## GitHub Secrets 配置

在 GitHub 仓库的 `Settings > Secrets and variables > Actions` 中添加以下 Secrets：

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `SERVER_HOST` | 服务器 IP 地址 | `45.32.17.107` |
| `SERVER_USER` | SSH 用户名 | `root` |
| `SERVER_PORT` | SSH 端口 | `22` |
| `SERVER_SSH_KEY` | SSH 私钥内容 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 | `your_root_password` |
| `MYSQL_USER` | MySQL 用户名 | `exam_user` |
| `MYSQL_PASSWORD` | MySQL 用户密码 | `your_secure_password` |
| `SECRET_KEY` | 应用密钥 | `your_secret_key_at_least_32_chars` |

### 生成 SSH 密钥对

```bash
# 在本地机器生成密钥对
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# 复制公钥到服务器
ssh-copy-id -i ~/.ssh/github_actions.pub root@45.32.17.107

# 复制私钥内容（用于 SERVER_SSH_KEY）
cat ~/.ssh/github_actions
```

### 配置 GitHub Environment

1. 进入仓库 `Settings > Environments`
2. 创建 `development` 环境（无需审批）
3. 创建 `production` 环境：
   - 启用 "Required reviewers"
   - 添加审批人（至少 1 人）

---

## 服务器初始化

### 1. 克隆仓库

```bash
# 进入应用目录
cd /opt/app

# 克隆仓库
git clone <your-repo-url> exam-system

# 进入项目目录
cd exam-system

# 切换到 main 分支
git checkout main
```

### 2. 创建环境变量文件

```bash
# 创建 .env 文件
cat > /opt/app/exam-system/.env << 'EOF'
# 数据库配置
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=exam_user
MYSQL_PASSWORD=your_secure_password_here
MYSQL_DATABASE=exam_system
MYSQL_ROOT_PASSWORD=your_root_password_here

# 应用安全配置
SECRET_KEY=your_secret_key_here_at_least_32_chars_long

# 前端配置
NEXT_PUBLIC_API_URL=http://45.32.17.107/api

# 域名配置
DOMAIN=45.32.17.107
EOF
```

### 3. 首次部署

```bash
# 使用生产配置启动服务
docker compose -f docker-compose.prod.yml up -d

# 执行数据库迁移
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 验证服务状态
docker compose -f docker-compose.prod.yml ps
```

---

## GitHub Actions 配置

### 测试环境 (deploy-dev.yml)

**触发条件**：push 到 `develop` 分支

**部署流程**：
1. SSH 连接服务器
2. 拉取最新代码 (`git pull origin develop`)
3. 构建 Docker 镜像
4. 执行数据库迁移
5. 启动服务
6. 健康检查

### 生产环境 (deploy-prod.yml)

**触发条件**：push 到 `main` 分支

**部署流程**：
1. 构建验证
2. **等待人工批准** (GitHub Environment Approval)
3. 备份数据库
4. SSH 连接服务器
5. 拉取最新代码
6. 构建 Docker 镜像
7. 执行数据库迁移
8. 启动服务
9. 验证部署

---

## Docker Compose 配置

### 生产环境配置 (docker-compose.prod.yml)

```yaml
version: '3.8'

services:
  # MySQL 数据库
  db:
    image: mysql:8.0
    container_name: exam-db-prod
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE:-exam_system}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - exam-network

  # 后端服务 (FastAPI)
  backend:
    build:
      context: ./backend
      dockerfile: ../docker/Dockerfile.backend
    container_name: exam-backend-prod
    restart: unless-stopped
    environment:
      DATABASE_URL: mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@db:3306/${MYSQL_DATABASE:-exam_system}
      SECRET_KEY: ${SECRET_KEY}
      CORS_ORIGINS: '["https://${DOMAIN}","http://localhost:3000"]'
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - uploads_data:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 30s
    networks:
      - exam-network

  # 前端服务 (Next.js)
  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/Dockerfile.frontend
    container_name: exam-frontend-prod
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_URL: https://${DOMAIN}/api
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    networks:
      - exam-network

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: exam-nginx-prod
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 3s
      retries: 3
    networks:
      - exam-network

volumes:
  mysql_data:
    driver: local
  uploads_data:
    driver: local

networks:
  exam-network:
    driver: bridge
```

---

## 环境变量配置

### .env.example

```bash
# ============================================
# 数据库配置
# ============================================
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=exam_user
MYSQL_PASSWORD=your_secure_password_here
MYSQL_DATABASE=exam_system
MYSQL_ROOT_PASSWORD=your_root_password_here

# ============================================
# 应用安全配置
# ============================================
# 应用密钥（用于 JWT 和其他加密用途）
# 必须至少 32 个字符
SECRET_KEY=your_secret_key_here_at_least_32_chars_long

# ============================================
# 前端配置
# ============================================
# 后端 API 地址（浏览器访问）
NEXT_PUBLIC_API_URL=https://yourdomain.com/api

# ============================================
# 域名配置
# ============================================
DOMAIN=yourdomain.com
```

### 环境变量说明

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `MYSQL_HOST` | MySQL 主机地址 | ✅ |
| `MYSQL_PORT` | MySQL 端口 | ✅ |
| `MYSQL_USER` | MySQL 用户名 | ✅ |
| `MYSQL_PASSWORD` | MySQL 用户密码 | ✅ |
| `MYSQL_DATABASE` | 数据库名称 | ✅ |
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 | ✅ |
| `SECRET_KEY` | 应用密钥（JWT 等） | ✅ |
| `NEXT_PUBLIC_API_URL` | 后端 API 地址 | ✅ |
| `DOMAIN` | 域名或 IP | ✅ |

---

## 数据库迁移配置

### 迁移流程

```
部署开始
    │
    ▼
┌──────────────────┐
│ 等待数据库就绪    │
│ (entrypoint.sh)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ alembic upgrade  │
│ head             │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 启动 FastAPI     │
└──────────────────┘
```

### 自动迁移机制

后端容器启动时会自动执行迁移：

1. **entrypoint.sh** 等待数据库就绪
2. 执行 `alembic upgrade head`
3. 启动 FastAPI 应用

### 手动迁移命令

```bash
# 执行迁移
docker compose exec backend alembic upgrade head

# 查看当前版本
docker compose exec backend alembic current

# 查看迁移历史
docker compose exec backend alembic history

# 回滚一个版本
docker compose exec backend alembic downgrade -1

# 回滚到指定版本
docker compose exec backend alembic downgrade <revision>
```

---

## 回滚方案

### 使用回滚脚本

```bash
# 进入脚本目录
cd /opt/app/scripts

# 查看可用版本
./rollback.sh list

# 查看当前状态
./rollback.sh status

# 手动备份数据库
./rollback.sh backup

# 回滚代码到指定版本
./rollback.sh code <commit_hash>

# 回滚数据库到指定版本
./rollback.sh db <revision>

# 完整回滚（代码 + 数据库）
./rollback.sh full <commit_hash> <revision>
```

### 手动回滚步骤

#### 1. 代码回滚

```bash
cd /opt/app/exam-system

# 查看提交历史
git log --oneline -20

# 回滚到指定版本
git checkout <commit_hash>

# 重新构建镜像
docker compose -f docker-compose.prod.yml build --no-cache

# 重启服务
docker compose -f docker-compose.prod.yml up -d
```

#### 2. 数据库回滚

```bash
# 先备份当前数据库
docker compose exec db mysqldump -u root -p<password> exam_system > backup.sql

# 查看迁移历史
docker compose exec backend alembic history

# 回滚到指定版本
docker compose exec backend alembic downgrade <revision>

# 或回滚一个版本
docker compose exec backend alembic downgrade -1
```

#### 3. 使用备份恢复数据库

```bash
# 查看可用备份
ls -lh /opt/app/backups/

# 解压备份
gunzip /opt/app/backups/db_backup_20240101_120000.sql.gz

# 恢复数据库
docker compose exec -T db mysql -u root -p<password> exam_system < /opt/app/backups/db_backup_20240101_120000.sql
```

---

## 运维建议

### 1. 监控

```bash
# 查看容器状态
docker compose ps

# 查看容器日志
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# 查看资源使用
docker stats
```

### 2. 日志管理

日志已配置 JSON 文件驱动，限制大小：
- 最大 10MB
- 保留 3 个文件

```bash
# 查看日志文件位置
docker inspect exam-backend-prod | grep -A 5 LogConfig
```

### 3. 备份策略

- 自动备份：每次生产部署前
- 保留时间：30 天
- 备份位置：`/opt/app/backups/`

```bash
# 手动备份
/opt/app/scripts/rollback.sh backup

# 设置定时备份（可选）
crontab -e
# 添加：0 2 * * * /opt/app/scripts/rollback.sh backup
```

### 4. 性能优化

```bash
# 清理未使用的 Docker 资源
docker system prune -a

# 清理旧镜像
docker image prune -a

# 清理构建缓存
docker builder prune
```

### 5. 安全建议

1. **定期更新密码**：MySQL、SECRET_KEY
2. **限制 SSH 访问**：使用密钥认证，禁用密码登录
3. **配置防火墙**：只开放 22、80、443 端口
4. **启用 HTTPS**：使用 Let's Encrypt 或 Cloudflare
5. **定期更新镜像**：修复安全漏洞

### 6. 故障排查

```bash
# 检查容器状态
docker compose ps

# 查看容器日志
docker compose logs backend

# 进入容器调试
docker compose exec backend bash

# 检查网络连接
docker compose exec backend curl http://db:3306

# 检查数据库连接
docker compose exec db mysql -u root -p -e "SHOW DATABASES;"
```

---

## 快速命令参考

```bash
# 启动服务
docker compose -f docker-compose.prod.yml up -d

# 停止服务
docker compose -f docker-compose.prod.yml down

# 重启服务
docker compose -f docker-compose.prod.yml restart

# 查看状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 执行迁移
docker compose exec backend alembic upgrade head

# 快速部署
/opt/app/scripts/deploy.sh

# 回滚操作
/opt/app/scripts/rollback.sh list
/opt/app/scripts/rollback.sh status
/opt/app/scripts/rollback.sh code <commit_hash>
```

---

## 文件清单

```
exam-system/
├── .github/
│   └── workflows/
│       ├── deploy-dev.yml      # 测试环境部署
│       └── deploy-prod.yml     # 生产环境部署
├── docker/
│   ├── Dockerfile.frontend     # 前端 Dockerfile
│   ├── Dockerfile.backend      # 后端 Dockerfile
│   ├── entrypoint.sh           # 后端启动脚本
│   └── rollback.sh             # 回滚脚本
├── docker-compose.yml          # 开发环境
├── docker-compose.prod.yml     # 生产环境
├── .env.example                # 环境变量模板
└── .env                        # 环境变量（不提交）
```
