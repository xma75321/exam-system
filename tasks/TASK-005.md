# TASK-005：用户登录 API

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：4 小时
- **依赖**：TASK-004
- **前置条件**：用户注册 API 已完成

## 任务描述
实现用户登录接口和获取当前用户接口，使用 JWT Token 认证。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/utils/__init__.py` | 创建 | 包初始化 |
| 2 | `backend/app/utils/security.py` | 创建 | JWT 工具函数 |
| 3 | `backend/app/routers/auth.py` | 修改 | 添加登录和获取当前用户端点 |
| 4 | `backend/app/schemas/user.py` | 修改 | 添加登录请求模型 |
| 5 | `backend/tests/test_auth_login.py` | 创建 | 登录测试 |

## 详细要求

### backend/app/utils/security.py
- `create_access_token(data: dict)`：创建 JWT Token，过期时间从配置读取
- `verify_token(token: str)`：验证并解析 Token
- `get_password_hash(password: str)`：bcrypt 加密
- `verify_password(plain: str, hashed: str)`：验证密码

### backend/app/routers/auth.py（修改）
新增端点：
- `POST /api/auth/login`：用户名+密码登录，返回 access_token
- `GET /api/auth/me`：需要 Authorization header，返回当前用户信息

### backend/app/schemas/user.py（修改）
新增：
- `UserLogin`：username(str), password(str)
- `TokenResponse`：access_token, token_type, expires_in

### backend/tests/test_auth_login.py
- 正确凭据登录返回 200 和 Token
- 错误密码返回 401
- 不存在的用户返回 401
- 带 Token 访问 /me 返回用户信息
- 无 Token 访问 /me 返回 401
- 过期 Token 返回 401

## 验收标准
1. `POST /api/auth/login` 正确凭据返回 JWT Token
2. 错误密码返回 401
3. `GET /api/auth/me` 带有效 Token 返回用户信息
4. `GET /api/auth/me` 无 Token 返回 401
5. Token 过期时间与配置一致
6. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_auth_login.py -v

# 手动测试
# 1. 登录
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"123456"}' | jq -r '.data.access_token')

# 2. 获取当前用户
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
# 预期：返回用户信息
```
