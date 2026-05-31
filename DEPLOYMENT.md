# CI/CD 自动化部署指南

## 目录
1. [概述](#概述)
2. [环境准备](#环境准备)
3. [GitHub Secrets 配置](#github-secrets-配置)
4. [部署流程](#部署流程)
5. [手动部署](#手动部署)
6. [常见问题](#常见问题)

---

## 概述

本项目使用 GitHub Actions 实现 CI/CD 自动化部署：

- **CI (持续集成)**: 代码推送时自动运行测试、代码检查、构建验证
- **CD (持续部署)**: 推送版本标签时自动构建 Docker 镜像并部署到服务器

### 部署架构

```
GitHub Repository
    ↓ (push code)
GitHub Actions CI
    ↓ (tests pass)
GitHub Actions CD
    ↓ (build & push)
Docker Registry (ghcr.io)
    ↓ (deploy)
Production Server
    ↓
Docker Compose (Nginx + Frontend + Backend + MySQL)
```

---

## 环境准备

### 1. 服务器要求

```bash
# 操作系统
Ubuntu 22.04 LTS / CentOS 8

# 最低配置
CPU: 2 核
内存: 4 GB
硬盘: 50 GB

# 必需软件
Docker 24.0+
Docker Compose v2.20+
Git 2.30+
```

### 2. 服务器初始化

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo apt install docker-compose-plugin

# 验证安装
docker --version
docker compose version

# 克隆项目
cd /opt
sudo mkdir exam-system
sudo chown $USER:$USER exam-system
git clone https://github.com/yourusername/exam-system.git
cd exam-system
```

---

## GitHub Secrets 配置

在 GitHub 仓库的 `Settings` → `Secrets and variables` → `Actions` 中添加以下 Secrets：

### Staging 环境

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `STAGING_HOST` | Staging 服务器 IP | `192.168.1.100` |
| `STAGING_USER` | SSH 用户名 | `deploy` |
| `STAGING_SSH_KEY` | SSH 私钥 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 | `YourRootPass123!` |
| `MYSQL_USER` | MySQL 用户名 | `exam_user` |
| `MYSQL_PASSWORD` | MySQL 密码 | `YourDBPass123!` |
| `SECRET_KEY` | JWT 密钥 | `your-super-secret-key-here` |

### Production 环境

| Secret 名称 | 说明 | 示例 |
|-------------|------|------|
| `PRODUCTION_HOST` | 生产服务器 IP | `10.0.0.100` |
| `PRODUCTION_USER` | SSH 用户名 | `deploy` |
| `PRODUCTION_SSH_KEY` | SSH 私钥 | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SLACK_WEBHOOK_URL` | Slack 通知 Webhook (可选) | `https://hooks.slack.com/services/...` |

### 生成 SSH 密钥

```bash
# 在本地生成 SSH 密钥对
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github-deploy

# 将公钥添加到服务器
ssh-copy-id -i ~/.ssh/github-deploy.pub user@server

# 复制私钥内容到 GitHub Secrets
cat ~/.ssh/github-deploy
```

---

## 部署流程

### 自动部署 (推荐)

1. **代码推送触发 CI**
   ```bash
   git add .
   git commit -m "feat: 新功能"
   git push origin main
   ```
   → 自动运行测试、代码检查

2. **发布版本触发 CD**
   ```bash
   # 创建版本标签
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
   → 自动构建镜像、部署到 Staging

3. **手动部署到 Production**
   - 进入 GitHub Actions 页面
   - 选择 "CD - 持续部署" 工作流
   - 点击 "Run workflow"
   - 选择 "production" 环境
   - 点击 "Run workflow" 按钮

### 部署状态查看

1. 进入 GitHub 仓库页面
2. 点击 "Actions" 标签
3. 查看工作流运行状态

---

## 手动部署

如果需要手动部署到服务器：

```bash
# SSH 登录服务器
ssh user@server

# 进入项目目录
cd /opt/exam-system

# 拉取最新代码
git pull origin main

# 创建环境变量文件
cat > .env << 'EOF'
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_USER=exam_user
MYSQL_PASSWORD=your_db_password
SECRET_KEY=your_secret_key
DOMAIN=yourdomain.com
VERSION=latest
EOF

# 启动服务
docker compose -f docker-compose.prod.yml up -d

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 执行数据库迁移
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 重启服务
docker compose -f docker-compose.prod.yml restart
```

---

## 常见问题

### 1. GitHub Actions 构建失败

**问题**: `Error: Cannot connect to the Docker daemon`

**解决**: 确保 GitHub Actions 有 Docker 权限
```yaml
# 在 workflow 文件中添加
permissions:
  contents: read
  packages: write
```

### 2. SSH 连接失败

**问题**: `Permission denied (publickey)`

**解决**: 
1. 检查 SSH 密钥是否正确添加到服务器
2. 检查 GitHub Secrets 中的 `*_SSH_KEY` 是否完整
3. 确保服务器 SSH 配置允许密钥登录

### 3. 数据库迁移失败

**问题**: `alembic.util.exc.CommandError: Can't locate revision`

**解决**:
```bash
# 进入后端容器
docker compose -f docker-compose.prod.yml exec backend bash

# 查看迁移状态
alembic current
alembic history

# 手动执行迁移
alembic upgrade head
```

### 4. Docker 镜像拉取失败

**问题**: `Error response from daemon: unauthorized`

**解决**: 确保 GitHub Token 有 `packages:write` 权限
```bash
# 手动登录 Docker Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### 5. 服务无法访问

**问题**: 浏览器无法打开网站

**解决**:
```bash
# 检查容器状态
docker compose -f docker-compose.prod.yml ps

# 检查日志
docker compose -f docker-compose.prod.yml logs nginx
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs backend

# 检查端口
netstat -tlnp | grep -E '80|443|3000|8000'

# 检查防火墙
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443
```

### 6. SSL 证书配置

**问题**: 需要配置 HTTPS

**解决**:
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 监控和日志

### 查看服务状态

```bash
# 查看所有容器状态
docker compose -f docker-compose.prod.yml ps

# 查看资源使用
docker stats

# 查看特定服务日志
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f nginx
```

### 数据库备份

```bash
# 手动备份
docker compose -f docker-compose.prod.yml exec db mysqldump -u root -p$MYSQL_ROOT_PASSWORD exam_system > backup_$(date +%Y%m%d_%H%M%S).sql

# 自动备份 (添加到 crontab)
0 2 * * * cd /opt/exam-system && docker compose -f docker-compose.prod.yml exec -T db mysqldump -u root -p$MYSQL_ROOT_PASSWORD exam_system > /backups/exam_system_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

---

## 回滚

如果部署出现问题，可以快速回滚：

```bash
# 查看历史版本
git tag -l

# 回滚到指定版本
git checkout v1.0.0

# 重新部署
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d

# 或者使用之前的镜像
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

*最后更新: 2026-05-31*
