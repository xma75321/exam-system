# 部署实战指南

> 基于实际部署经验编写，记录所有踩过的坑。**部署前必读**。

---

## 一、架构概览

```
浏览器
  ↓
Nginx (80)
  ├── /_next/* → 前端 (3000)
  └── /api/*   → 后端 (8000)
                  ↓
                MySQL (3306)
```

**技术栈**：
- 前端：Next.js 14 + TypeScript
- 后端：FastAPI + SQLAlchemy
- 数据库：MySQL 8.0
- 部署：Docker Compose + GitHub Actions

---

## 二、必须避免的 8 个坑

### 坑 1：Next.js 环境变量不生效 ⚠️ 最常见

**现象**：前端请求 `http://localhost:8000/api`，浏览器报 `Failed to fetch`

**原因**：`NEXT_PUBLIC_*` 变量在**构建时**注入，不是运行时

**错误做法**：
```yaml
# ❌ 只在运行时设置，构建时没有
frontend:
  environment:
    NEXT_PUBLIC_API_URL: http://45.32.17.107/api
```

**正确做法**：
```dockerfile
# Dockerfile.frontend
ARG NEXT_PUBLIC_API_URL          # 声明构建参数
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}  # 设置环境变量
RUN npm run build                # 构建时注入
```

```yaml
# docker-compose.yml
frontend:
  build:
    args:
      NEXT_PUBLIC_API_URL: http://${DOMAIN}/api  # 传递构建参数
  environment:
    NEXT_PUBLIC_API_URL: http://${DOMAIN}/api    # 运行时也需要
```

**验证方法**：
```bash
docker exec <container> printenv NEXT_PUBLIC_API_URL
# 应输出：http://45.32.17.107/api
```

---

### 坑 2：密码中的特殊字符被转义

**现象**：数据库连接失败，日志显示 `Access denied`

**原因**：Shell 将 `$`、`!` 等字符解释为变量

**错误示例**：
```bash
MYSQL_PASSWORD=MyP@ss$word  # $word 被解释为变量，实际密码变成 MyP@ss
```

**正确做法**：
```bash
# 方案 1：避免特殊字符（推荐）
MYSQL_PASSWORD=MyPAssword123

# 方案 2：使用单引号
MYSQL_PASSWORD='MyP@ss$word'

# 方案 3：使用双引号并转义
MYSQL_PASSWORD="MyP@ss\$word"
```

**经验**：生成密码时只使用字母和数字，避免 `$`、`!`、`#`、`&` 等字符

---

### 坑 3：CORS 配置不一致

**现象**：浏览器报 `CORS policy blocked`，但 curl 测试正常

**原因**：前端 Origin 与后端 CORS_ORIGINS 不匹配

**排查步骤**：
```bash
# 1. 检查前端 Origin
# 浏览器访问 http://45.32.17.107，Origin 就是 http://45.32.17.107

# 2. 检查后端 CORS_ORIGINS
docker exec backend printenv CORS_ORIGINS

# 3. 测试 OPTIONS 预检请求
curl -X OPTIONS -H "Origin: http://45.32.17.107" \
  -H "Access-Control-Request-Method: POST" \
  http://localhost/api/auth/register -v
```

**正确配置**：
```yaml
# docker-compose.yml
environment:
  CORS_ORIGINS: '["http://${DOMAIN}","http://localhost:3000"]'
```

```python
# backend/app/config.py
@field_validator("CORS_ORIGINS", mode="before")
@classmethod
def parse_cors_origins(cls, v):
    if isinstance(v, str):
        return json.loads(v)
    return v
```

**关键点**：
- `http` vs `https` 必须一致
- 域名/IP 必须完全匹配
- JSON 格式必须正确

---

### 坑 4：entrypoint.sh 语法错误

**现象**：后端容器启动失败，日志显示 `syntax error near unexpected token`

**原因**：使用多行 Python heredoc 导致 Shell 解析失败

**错误示例**：
```bash
#!/bin/bash
python << 'EOF'
import something
if condition:
    do_something()  # ❌ Shell 无法正确解析
EOF
```

**正确做法**：
```bash
#!/bin/bash
# 使用单行 Python 命令
python -c "import something; do_something() if condition else None"

# 或者写成 Python 脚本文件
python /app/scripts/init.py
```

**验证方法**：
```bash
bash -n entrypoint.sh  # 检查语法
```

---

### 坑 5：端口映射缺失

**现象**：容器运行正常，但外部无法访问

**原因**：`docker-compose.yml` 没有配置 `ports`

**正确配置**：
```yaml
services:
  frontend:
    ports:
      - "3000:3000"
  backend:
    ports:
      - "8000:8000"
  nginx:
    ports:
      - "80:80"
      - "443:443"
```

**验证方法**：
```bash
# 检查端口监听
netstat -tlnp | grep -E ':(80|443|3000|8000)'

# 检查容器端口
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

---

### 坑 6：文件/目录缺失

**现象**：Docker 构建失败，`COPY failed: file not found`

**常见缺失**：
- `frontend/public/` 目录（Next.js 需要）
- `frontend/package-lock.json`（npm ci 需要）
- 配置文件

**解决方案**：
```bash
# 创建必要目录
mkdir -p frontend/public
touch frontend/public/.gitkeep

# 生成 package-lock.json
cd frontend && npm install

# 提交到 Git
git add frontend/public/.gitkeep frontend/package-lock.json
```

---

### 坑 7：Nginx 配置问题

**现象**：Nginx 容器启动失败或代理无效

**常见原因**：
1. 配置文件路径错误
2. SSL 参数文件缺失
3. 语法错误

**解决方案**：
```yaml
# docker-compose.yml
nginx:
  volumes:
    - ./docker/nginx.prod.conf:/etc/nginx/nginx.conf:ro
  # 不要挂载不存在的 SSL 文件
```

**验证方法**：
```bash
# 检查配置语法
docker exec nginx nginx -t

# 查看错误日志
docker logs nginx
```

---

### 坑 8：数据库健康检查配置错误

**现象**：后端启动时报 `Connection refused`，但数据库容器已运行

**原因**：数据库还在初始化，后端就开始连接了

**正确配置**：
```yaml
# docker-compose.yml
db:
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 30s

backend:
  depends_on:
    db:
      condition: service_healthy  # 等待数据库健康
```

---

## 三、部署流程

### 3.1 首次部署

```bash
# 1. 准备服务器
ssh root@your-server-ip
apt update && apt install -y docker.io docker-compose-plugin

# 2. 克隆代码
git clone https://github.com/your-username/exam-system.git /opt/app/exam-system
cd /opt/app/exam-system

# 3. 配置环境变量
cp .env.example .env
vim .env
# 修改以下内容：
# - MYSQL_ROOT_PASSWORD（避免特殊字符）
# - MYSQL_PASSWORD（避免特殊字符）
# - SECRET_KEY
# - DOMAIN（你的域名或 IP）

# 4. 构建并启动
docker compose -f docker-compose.prod.yml up -d --build

# 5. 检查状态
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

### 3.2 更新部署

```bash
# 1. 拉取最新代码
cd /opt/app/exam-system
git pull origin main

# 2. 重新构建（如果有 Dockerfile 或依赖变更）
docker compose -f docker-compose.prod.yml up -d --build

# 3. 仅重启（如果只是代码变更）
docker compose -f docker-compose.prod.yml up -d
```

### 3.3 回滚部署

```bash
# 1. 查看历史版本
git log --oneline -10

# 2. 回滚到指定版本
git checkout <commit-hash>

# 3. 重新构建
docker compose -f docker-compose.prod.yml up -d --build

# 4. 验证
docker compose -f docker-compose.prod.yml ps
```

---

## 四、部署后验证清单

### 4.1 容器状态检查

```bash
# 所有容器应该为 "Up" 状态
docker compose -f docker-compose.prod.yml ps

# 检查健康状态
docker inspect exam-backend-prod --format="{{.State.Health.Status}}"
docker inspect exam-frontend-prod --format="{{.State.Health.Status}}"
docker inspect exam-db-prod --format="{{.State.Health.Status}}"
```

### 4.2 API 连通性测试

```bash
# 后端健康检查
curl http://localhost:8000/health
# 期望输出：{"status":"ok"}

# 通过 Nginx 测试
curl http://localhost/api/health
# 期望输出：{"status":"ok"}

# 测试注册接口
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}' \
  http://localhost/api/auth/register
# 期望输出：{"code":0,"data":{...},"message":"注册成功"}
```

### 4.3 CORS 测试

```bash
# 测试预检请求
curl -X OPTIONS -H "Origin: http://your-domain.com" \
  -H "Access-Control-Request-Method: POST" \
  http://localhost/api/auth/register -v
# 期望输出：HTTP/1.1 200 OK，包含 CORS 头
```

### 4.4 前端测试

```bash
# 检查前端页面加载
curl -s http://localhost:3000 | head -5
# 期望输出：HTML 内容

# 检查环境变量注入
docker exec exam-frontend-prod printenv NEXT_PUBLIC_API_URL
# 期望输出：http://your-domain/api
```

### 4.5 浏览器测试

1. 清除浏览器缓存（Ctrl + Shift + Delete）
2. 或使用隐身模式（Ctrl + Shift + N）
3. 访问 http://your-domain
4. 按 F12 打开开发者工具
5. 检查 Console 标签是否有错误
6. 测试注册/登录功能

---

## 五、问题排查速查表

### 5.1 容器相关

```bash
# 查看所有容器
docker ps -a

# 查看容器日志
docker logs <container-name>
docker logs --tail=100 <container-name>
docker logs -f <container-name>  # 实时查看

# 进入容器调试
docker exec -it <container-name> sh

# 查看容器环境变量
docker exec <container-name> printenv

# 查看容器资源使用
docker stats
```

### 5.2 网络相关

```bash
# 检查端口监听
netstat -tlnp | grep -E ':(80|443|3000|8000)'

# 测试内部连通性
docker exec backend ping db
docker exec nginx curl http://backend:8000/health

# 查看 Docker 网络
docker network ls
docker network inspect exam-system_exam-network
```

### 5.3 数据库相关

```bash
# 进入数据库
docker exec -it exam-db-prod mysql -u root -p

# 查看数据库日志
docker logs exam-db-prod

# 检查数据库健康状态
docker inspect exam-db-prod --format="{{.State.Health.Status}}"
```

---

## 六、环境变量参考

### .env 文件模板

```bash
# 数据库配置
MYSQL_ROOT_PASSWORD=your_root_password_here
MYSQL_USER=exam_user
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=exam_system

# 应用配置
SECRET_KEY=your_secret_key_here
DOMAIN=your-domain.com  # 或 IP 地址，如 45.32.17.107

# CORS 配置（可选，默认自动生成）
# CORS_ORIGINS=["http://your-domain.com","http://localhost:3000"]
```

### 关键点

- **密码**：只使用字母和数字，避免 `$`、`!`、`#`、`&`
- **DOMAIN**：填写域名或 IP，不要加 `http://`
- **SECRET_KEY**：使用随机字符串，至少 32 位

---

## 七、GitHub Actions CI/CD

### 7.1 工作流程

```
push to develop → 自动部署到测试环境
push to main    → 需要审批 → 部署到生产环境
```

### 7.2 必需的 Secrets

在 GitHub 仓库设置中配置：

```
Settings → Secrets and variables → Actions → New repository secret
```

需要添加：
- `SERVER_HOST`：服务器 IP
- `SERVER_USER`：SSH 用户名
- `SERVER_PASSWORD`：SSH 密码
- `MYSQL_ROOT_PASSWORD`：与服务器 .env 一致
- `MYSQL_PASSWORD`：与服务器 .env 一致
- `SECRET_KEY`：与服务器 .env 一致

### 7.3 环境审批

生产环境部署需要审批：

```
Settings → Environments → production → Required reviewers
```

添加审批人，每次部署 main 分支时需要审批。

---

## 八、常见错误码

| 错误码 | 含义 | 排查方向 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求体格式 |
| 401 | 未认证 | 检查 Token 是否有效 |
| 403 | 无权限 | 检查 CORS 配置 |
| 404 | 资源不存在 | 检查路由配置 |
| 500 | 服务器错误 | 查看后端日志 |
| 502 | 网关错误 | 后端容器未启动 |
| 503 | 服务不可用 | 容器健康检查失败 |

---

## 九、性能优化建议

### 9.1 Docker 镜像优化

```dockerfile
# 使用多阶段构建
FROM node:22-alpine AS builder
# ... 构建阶段

FROM node:22-alpine AS runner
# ... 运行阶段，只复制必要文件
```

### 9.2 日志管理

```yaml
# docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 9.3 数据备份

```bash
# 备份数据库
docker exec exam-db-prod mysqldump -u root -p exam_system > backup.sql

# 恢复数据库
docker exec -i exam-db-prod mysql -u root -p exam_system < backup.sql
```

---

## 十、联系与支持

遇到问题时：
1. 先查看本文档
2. 检查容器日志：`docker compose logs -f`
3. 搜索错误信息
4. 提交 GitHub Issue

---

**最后更新**：2026-05-31
**基于实际部署经验编写**
