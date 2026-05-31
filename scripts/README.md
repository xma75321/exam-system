# 一键部署指南

> 从零开始，一条命令部署整个考试系统

---

## 快速开始

### 方式一：一键部署（推荐）

```bash
curl -sSL https://raw.githubusercontent.com/xma75321/exam-system/main/scripts/quick-deploy.sh | bash -s -- --domain=your-domain.com
```

**参数说明**：
- `--domain=your-domain.com`：你的域名或 IP 地址（必填）
- `--repo=<url>`：Git 仓库地址（可选，默认使用官方仓库）
- `--dir=<path>`：安装目录（可选，默认 `/opt/app/exam-system`）

**示例**：
```bash
# 使用域名
curl -sSL https://raw.githubusercontent.com/xma75321/exam-system/main/scripts/quick-deploy.sh | bash -s -- --domain=exam.example.com

# 使用 IP
curl -sSL https://raw.githubusercontent.com/xma75321/exam-system/main/scripts/quick-deploy.sh | bash -s -- --domain=45.32.17.107

# 使用自定义仓库
curl -sSL https://raw.githubusercontent.com/xma75321/exam-system/main/scripts/quick-deploy.sh | bash -s -- --domain=exam.example.com --repo=https://github.com/your-username/exam-system.git
```

---

### 方式二：分步部署

#### 步骤 1：初始化服务器

```bash
curl -sSL https://raw.githubusercontent.com/xma75321/exam-system/main/scripts/init-server.sh | bash
```

#### 步骤 2：克隆代码

```bash
git clone https://github.com/xma75321/exam-system.git /opt/app/exam-system
cd /opt/app/exam-system
```

#### 步骤 3：配置环境变量

```bash
cp .env.example .env
vim .env
```

**必须修改的配置**：
```bash
MYSQL_ROOT_PASSWORD=your_root_password  # 数据库 root 密码
MYSQL_PASSWORD=your_password            # 数据库用户密码
SECRET_KEY=your_secret_key              # 应用密钥
DOMAIN=your-domain.com                  # 域名或 IP
```

#### 步骤 4：部署应用

```bash
./scripts/deploy.sh
```

---

## 脚本说明

### 1. init-server.sh

**用途**：初始化新服务器环境

**功能**：
- 更新系统包
- 安装 Docker 和 Docker Compose
- 配置防火墙（开放 22、80、443 端口）
- 安装常用工具（git、curl、wget 等）
- 创建应用目录

**使用**：
```bash
curl -sSL https://raw.githubusercontent.com/xma75321/exam-system/main/scripts/init-server.sh | bash
```

---

### 2. deploy.sh

**用途**：构建并启动所有服务

**功能**：
- 检查 .env 配置
- 检查密码安全性
- 拉取最新代码
- 构建 Docker 镜像
- 启动所有服务
- 等待服务就绪
- 验证部署状态

**使用**：
```bash
cd /opt/app/exam-system
./scripts/deploy.sh
```

---

### 3. update.sh

**用途**：快速更新部署

**功能**：
- 拉取最新代码
- 检测 Docker 配置变更
- 自动决定重新构建或仅重启
- 验证更新状态

**使用**：
```bash
cd /opt/app/exam-system
./scripts/update.sh
```

---

### 4. quick-deploy.sh

**用途**：全新服务器一键部署

**功能**：
- 初始化服务器
- 克隆代码
- 自动生成密码
- 配置环境变量
- 部署应用
- 保存部署信息

**使用**：
```bash
curl -sSL https://raw.githubusercontent.com/xma75321/exam-system/main/scripts/quick-deploy.sh | bash -s -- --domain=your-domain.com
```

---

## 部署后验证

### 1. 访问应用

```bash
# 浏览器访问
http://your-domain.com
```

### 2. 检查容器状态

```bash
cd /opt/app/exam-system
docker compose -f docker-compose.prod.yml ps
```

### 3. 检查健康状态

```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端页面
curl -s http://localhost:3000 | head -3
```

### 4. 查看日志

```bash
# 查看所有日志
docker compose -f docker-compose.prod.yml logs -f

# 查看指定服务日志
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
```

---

## 常见问题

### Q1: 部署失败怎么办？

```bash
# 查看日志
docker compose -f docker-compose.prod.yml logs

# 检查容器状态
docker ps -a

# 重新部署
./scripts/deploy.sh
```

### Q2: 如何更新应用？

```bash
cd /opt/app/exam-system
./scripts/update.sh
```

### Q3: 如何修改配置？

```bash
# 编辑环境变量
vim .env

# 重新部署
./scripts/deploy.sh
```

### Q4: 如何备份数据？

```bash
# 备份数据库
docker exec exam-db-prod mysqldump -u root -p exam_system > backup.sql

# 恢复数据库
docker exec -i exam-db-prod mysql -u root -p exam_system < backup.sql
```

### Q5: 如何查看密码？

```bash
cat /root/exam-system-credentials.txt
```

---

## 安全建议

### 1. 修改默认密码

部署后立即修改默认密码：

```bash
# 编辑 .env 文件
vim .env

# 修改密码
MYSQL_ROOT_PASSWORD=new_password
MYSQL_PASSWORD=new_password
SECRET_KEY=new_secret_key

# 重新部署
./scripts/deploy.sh
```

### 2. 配置 HTTPS

使用 Let's Encrypt 配置 HTTPS：

```bash
# 安装 Certbot
apt install -y certbot

# 获取证书
certbot certonly --standalone -d your-domain.com

# 配置 Nginx
vim docker/nginx.prod.conf
```

### 3. 限制 SSH 访问

```bash
# 编辑 SSH 配置
vim /etc/ssh/sshd_config

# 修改以下配置
PermitRootLogin no
PasswordAuthentication no

# 重启 SSH
systemctl restart sshd
```

---

## 目录结构

```
/opt/app/exam-system/
├── scripts/
│   ├── init-server.sh      # 服务器初始化
│   ├── deploy.sh           # 部署脚本
│   ├── update.sh           # 更新脚本
│   └── quick-deploy.sh     # 一键部署
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.prod.conf
├── backend/                # 后端代码
├── frontend/               # 前端代码
├── docker-compose.prod.yml
├── .env                    # 环境变量
└── docs/
    ├── DEPLOYMENT_GUIDE.md
    └── DEPLOY_CHECKLIST.md
```

---

## 技术支持

遇到问题时：
1. 查看本文档
2. 查看部署指南：`docs/DEPLOYMENT_GUIDE.md`
3. 查看检查清单：`docs/DEPLOY_CHECKLIST.md`
4. 提交 GitHub Issue

---

**最后更新**：2026-05-31
