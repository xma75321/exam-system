# 部署前检查清单

> 每次部署前，请逐项检查以下内容。

---

## 快速检查（5 分钟）

### ✅ 服务器环境
- [ ] Docker 已安装：`docker --version`
- [ ] Docker Compose 已安装：`docker compose version`
- [ ] 端口未被占用：`lsof -i :80`、`lsof -i :443`
- [ ] 磁盘空间充足：`df -h`

### ✅ 代码准备
- [ ] `.gitignore` 包含：`.env`、`node_modules`、`__pycache__`、`uploads/`
- [ ] `frontend/public/` 目录存在
- [ ] 敏感信息未提交

### ✅ Docker 配置
- [ ] `docker-compose.yml` 包含 `ports` 配置
- [ ] `docker-compose.yml` 包含 `healthcheck` 配置
- [ ] `docker-compose.yml` 包含 `depends_on` 配置
- [ ] `Dockerfile` 使用非 root 用户

### ✅ 环境变量
- [ ] `.env` 文件存在且配置正确
- [ ] 数据库密码无特殊字符（或已正确转义）
- [ ] `NEXT_PUBLIC_*` 变量在 Dockerfile 中声明为 `ARG`

---

## 详细检查（首次部署）

### 1. Next.js 环境变量
```bash
# 确认 Dockerfile 包含：
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# 确认 docker-compose.yml 包含：
build:
  args:
    NEXT_PUBLIC_API_URL: http://${DOMAIN}/api
```

### 2. CORS 配置
```bash
# 确认前端 Origin 与后端 CORS_ORIGINS 匹配
# 前端：http://your-domain.com
# 后端：["http://your-domain.com"]
```

### 3. 数据库连接
```bash
# 确认 DATABASE_URL 格式正确
DATABASE_URL=mysql+pymysql://user:password@db:3306/database
```

### 4. Nginx 配置
```bash
# 确认配置文件存在
ls -la docker/nginx.prod.conf

# 确认无 SSL 参数依赖（除非已配置）
```

---

## 部署后验证

### 1. 容器状态
```bash
docker compose -f docker-compose.prod.yml ps
# 所有容器应为 "Up" 状态
```

### 2. 健康检查
```bash
# 后端健康
curl http://localhost:8000/health

# 前端加载
curl http://localhost:3000

# Nginx 代理
curl http://localhost/api/health
```

### 3. API 测试
```bash
# 测试注册接口
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}' \
  http://localhost/api/auth/register

# 测试 CORS
curl -X OPTIONS -H "Origin: http://your-domain.com" \
  -H "Access-Control-Request-Method: POST" \
  http://localhost/api/auth/register -v
```

### 4. 浏览器测试
- [ ] 页面正常加载
- [ ] 注册/登录功能正常
- [ ] 控制台无错误

---

## 常见问题速查

| 问题 | 检查项 |
|------|--------|
| 页面空白 | `NEXT_PUBLIC_API_URL` 是否正确注入 |
| Failed to fetch | CORS 配置、API 地址、网络连通性 |
| 502 Bad Gateway | 后端容器是否启动、端口映射 |
| 数据库连接失败 | 数据库容器健康状态、连接字符串 |

---

**最后更新**：2026-05-31
