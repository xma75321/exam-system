# 部署前检查清单

> 每次部署前，请逐项检查。基于实际踩坑经验编写。

---

## 快速检查（5 分钟）

### ✅ 服务器环境
- [ ] Docker 已安装：`docker --version`
- [ ] Docker Compose 已安装：`docker compose version`
- [ ] 端口未被占用：`lsof -i :80`、`lsof -i :443`
- [ ] 磁盘空间充足：`df -h`

### ✅ 代码准备
- [ ] `.gitignore` 包含：`.env`、`node_modules`、`__pycache__`、`uploads/`
- [ ] `frontend/public/` 目录存在（添加 `.gitkeep`）
- [ ] 敏感信息未提交

### ✅ 环境变量
- [ ] `.env` 文件存在且配置正确
- [ ] **密码无特殊字符**（避免 `$`、`!`、`#`、`&`）
- [ ] `DOMAIN` 填写正确（不带 `http://`）

### ✅ Docker 配置
- [ ] `docker-compose.yml` 包含 `ports` 配置
- [ ] `docker-compose.yml` 包含 `healthcheck` 配置
- [ ] `docker-compose.yml` 包含 `depends_on` 配置

---

## 详细检查（首次部署）

### 1. Next.js 环境变量 ⚠️ 最重要

```bash
# 确认 Dockerfile 包含：
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# 确认 docker-compose.yml 包含：
build:
  args:
    NEXT_PUBLIC_API_URL: http://${DOMAIN}/api
```

**为什么**：`NEXT_PUBLIC_*` 变量在构建时注入，运行时设置无效

### 2. CORS 配置

```bash
# 确认前端 Origin 与后端 CORS_ORIGINS 匹配
# 前端：http://your-domain.com
# 后端：["http://your-domain.com"]
```

**为什么**：`http` vs `https` 不一致会导致 CORS 错误

### 3. 数据库健康检查

```yaml
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
      condition: service_healthy
```

**为什么**：数据库初始化需要时间，后端需要等待

### 4. entrypoint.sh 语法

```bash
# 检查语法
bash -n backend/entrypoint.sh

# 避免多行 Python heredoc，使用单行命令
```

**为什么**：多行 heredoc 在 Shell 中容易出错

---

## 部署后验证

### 1. 容器状态
```bash
docker compose -f docker-compose.prod.yml ps
# 所有容器应为 "Up" 状态
```

### 2. 健康检查
```bash
# 后端
curl http://localhost:8000/health

# 前端
curl -s http://localhost:3000 | head -3

# Nginx
curl http://localhost/api/health
```

### 3. 环境变量验证
```bash
# 检查前端 API 地址是否正确注入
docker exec exam-frontend-prod printenv NEXT_PUBLIC_API_URL
# 应输出：http://your-domain/api
```

### 4. CORS 测试
```bash
curl -X OPTIONS -H "Origin: http://your-domain.com" \
  -H "Access-Control-Request-Method: POST" \
  http://localhost/api/auth/register -v
```

### 5. 浏览器测试
- [ ] 清除缓存（Ctrl + Shift + Delete）或使用隐身模式
- [ ] 页面正常加载
- [ ] 注册/登录功能正常
- [ ] 控制台无错误

---

## 常见问题速查

| 问题 | 检查项 |
|------|--------|
| Failed to fetch | `NEXT_PUBLIC_API_URL` 是否正确注入 |
| CORS blocked | 前端 Origin 与后端 CORS_ORIGINS 是否一致 |
| 502 Bad Gateway | 后端容器是否启动、端口映射 |
| 数据库连接失败 | 密码是否有特殊字符、数据库健康状态 |
| 容器启动失败 | 检查日志：`docker logs <container>` |

---

**最后更新**：2026-05-31
