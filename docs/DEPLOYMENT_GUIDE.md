# CI/CD 部署指南与踩坑记录

> 本文档记录部署过程中遇到的问题和解决方案，**下次部署前请先阅读本文档**。

---

## 一、部署前检查清单

### 1.1 服务器准备
- [ ] Docker 已安装（版本 ≥ 20.10）
- [ ] Docker Compose 已安装（版本 ≥ 2.0）
- [ ] 防火墙已开放端口：22（SSH）、80（HTTP）、443（HTTPS）
- [ ] SSH 已配置密钥登录（推荐）

### 1.2 代码准备
- [ ] `.gitignore` 已配置（排除 `.env`、`node_modules`、`__pycache__`、`uploads/`）
- [ ] `frontend/public/` 目录存在（即使为空，添加 `.gitkeep`）
- [ ] 敏感信息不提交到 Git

### 1.3 Docker 配置检查
- [ ] `docker-compose.yml` 包含完整配置：
  - `ports`：端口映射
  - `volumes`：数据持久化
  - `healthcheck`：健康检查
  - `depends_on`：启动顺序
  - `networks`：容器通信
- [ ] `Dockerfile` 使用非 root 用户
- [ ] 健康检查配置合理

---

## 二、常见问题与解决方案

### 2.1 Next.js 环境变量问题 ⚠️ 重要

**问题**：`NEXT_PUBLIC_*` 变量在运行时设置无效

**原因**：Next.js 的 `NEXT_PUBLIC_*` 变量在**构建时**嵌入代码，不是运行时

**解决方案**：
```dockerfile
# Dockerfile.frontend
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build
```

```yaml
# docker-compose.yml
frontend:
  build:
    args:
      NEXT_PUBLIC_API_URL: http://${DOMAIN}/api
  environment:
    NEXT_PUBLIC_API_URL: http://${DOMAIN}/api  # 运行时也需要
```

**验证方法**：
```bash
docker exec <container> printenv NEXT_PUBLIC_API_URL
```

---

### 2.2 Shell 变量转义问题

**问题**：密码中的 `$`、`!` 等特殊字符被 Shell 解释

**错误示例**：
```bash
MYSQL_PASSWORD=MyP@ss$word  # $word 被解释为变量
```

**解决方案**：
```bash
# 方案 1：使用单引号
MYSQL_PASSWORD='MyP@ss$word'

# 方案 2：避免特殊字符（推荐）
MYSQL_PASSWORD=MyPAssword123

# 方案 3：使用双引号并转义
MYSQL_PASSWORD="MyP@ss\$word"
```

---

### 2.3 CORS 配置不一致

**问题**：前端请求被 CORS 策略阻止

**排查步骤**：
1. 检查浏览器控制台错误信息
2. 确认前端 Origin 与后端 CORS_ORIGINS 匹配
3. 测试 OPTIONS 预检请求

**解决方案**：
```python
# backend/app/config.py
CORS_ORIGINS: list[str] = ["http://localhost:3000"]

@field_validator("CORS_ORIGINS", mode="before")
@classmethod
def parse_cors_origins(cls, v):
    if isinstance(v, str):
        return json.loads(v)
    return v
```

```yaml
# docker-compose.yml
environment:
  CORS_ORIGINS: '["http://${DOMAIN}","http://localhost:3000"]'
```

**验证方法**：
```bash
# 测试 CORS 预检
curl -X OPTIONS -H "Origin: http://your-domain.com" \
  -H "Access-Control-Request-Method: POST" \
  http://localhost/api/auth/register -v
```

---

### 2.4 Nginx 配置问题

**问题**：Nginx 无法启动或代理失败

**常见原因**：
1. 配置文件路径错误
2. SSL 参数文件缺失
3. 端口冲突

**解决方案**：
```yaml
# docker-compose.yml
nginx:
  volumes:
    - ./docker/nginx.prod.conf:/etc/nginx/nginx.conf:ro
  # 移除 SSL 参数挂载（如果不需要）
```

**验证方法**：
```bash
# 检查 Nginx 配置
docker exec nginx nginx -t

# 查看 Nginx 日志
docker logs nginx
```

---

### 2.5 数据库连接问题

**问题**：后端无法连接数据库

**排查步骤**：
1. 检查数据库容器是否健康
2. 检查环境变量是否正确
3. 检查网络配置

**解决方案**：
```yaml
# docker-compose.yml
backend:
  environment:
    DATABASE_URL: mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@db:3306/${MYSQL_DATABASE}
  depends_on:
    db:
      condition: service_healthy  # 等待数据库健康
```

**验证方法**：
```bash
# 检查数据库健康状态
docker inspect db --format="{{.State.Health.Status}}"

# 测试数据库连接
docker exec backend python -c "from app.database import engine; print(engine.connect())"
```

---

### 2.6 端口映射缺失

**问题**：容器运行但外部无法访问

**解决方案**：
```yaml
# docker-compose.yml
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

---

### 2.7 文件/目录缺失

**问题**：Docker COPY 失败

**常见缺失**：
- `frontend/public/` 目录
- `frontend/package-lock.json`
- 配置文件

**解决方案**：
```bash
# 创建必要目录
mkdir -p frontend/public
touch frontend/public/.gitkeep

# 确保 package-lock.json 存在
cd frontend && npm install
```

---

## 三、部署流程

### 3.1 首次部署
```bash
# 1. 克隆代码
git clone <repo-url> /opt/app/exam-system
cd /opt/app/exam-system

# 2. 配置环境变量
cp .env.example .env
vim .env  # 修改密码、域名等

# 3. 构建并启动
docker compose -f docker-compose.prod.yml up -d --build

# 4. 检查状态
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

### 3.2 更新部署
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建（如果有 Dockerfile 变更）
docker compose -f docker-compose.prod.yml up -d --build

# 3. 仅重启（如果只是代码变更）
docker compose -f docker-compose.prod.yml up -d
```

### 3.3 回滚部署
```bash
# 1. 查看历史版本
git log --oneline

# 2. 回滚到指定版本
git checkout <commit-hash>

# 3. 重新构建
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 四、排查命令速查

### 容器状态
```bash
# 查看所有容器
docker ps -a

# 查看容器健康状态
docker inspect <container> --format="{{.State.Health.Status}}"

# 查看容器资源使用
docker stats
```

### 日志查看
```bash
# 查看所有服务日志
docker compose -f docker-compose.prod.yml logs -f

# 查看指定服务日志
docker compose -f docker-compose.prod.yml logs -f backend

# 查看最近 100 行
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

### 网络测试
```bash
# 测试 API 连通性
curl -s http://localhost:8000/health

# 测试 CORS
curl -X OPTIONS -H "Origin: http://your-domain.com" \
  -H "Access-Control-Request-Method: POST" \
  http://localhost/api/auth/register -v

# 测试数据库连接
docker exec backend python -c "from app.database import engine; print(engine.connect())"
```

### 环境变量检查
```bash
# 查看容器环境变量
docker exec <container> printenv

# 查看指定变量
docker exec <container> printenv NEXT_PUBLIC_API_URL
```

---

## 五、最佳实践

### 5.1 环境变量管理
- 使用 `.env.example` 作为模板
- 不同环境使用不同的 `.env` 文件
- 敏感信息不提交到 Git

### 5.2 Docker 镜像优化
- 使用多阶段构建
- 使用非 root 用户
- 合理设置健康检查

### 5.3 日志管理
- 配置日志轮转
- 集中收集日志
- 设置告警规则

### 5.4 备份策略
- 数据库定期备份
- 重要配置文件备份
- 测试恢复流程

---

## 六、常见错误码

| 错误码 | 含义 | 可能原因 |
|--------|------|----------|
| 400 | 请求参数错误 | 请求体格式错误 |
| 401 | 未认证 | Token 无效或过期 |
| 403 | 无权限 | CORS 策略阻止 |
| 404 | 资源不存在 | 路径错误或服务未启动 |
| 500 | 服务器内部错误 | 后端代码异常 |
| 502 | 网关错误 | 后端服务未启动 |
| 503 | 服务不可用 | 容器未启动或健康检查失败 |

---

## 七、联系方式

遇到问题时：
1. 先查看本文档
2. 检查日志：`docker compose logs -f`
3. 搜索错误信息
4. 联系运维人员

---

**最后更新**：2026-05-31
**维护人**：DevOps Team
