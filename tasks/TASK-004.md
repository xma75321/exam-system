# TASK-004：用户注册 API

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：4 小时
- **依赖**：TASK-001, TASK-003
- **前置条件**：数据库模型已创建

## 任务描述
实现用户注册接口，包括请求验证、密码加密和用户创建。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/schemas/__init__.py` | 创建 | 包初始化 |
| 2 | `backend/app/schemas/user.py` | 创建 | 用户 Pydantic 模型 |
| 3 | `backend/app/routers/__init__.py` | 创建 | 包初始化 |
| 4 | `backend/app/routers/auth.py` | 创建 | 认证路由（注册） |
| 5 | `backend/tests/test_auth_register.py` | 创建 | 注册测试 |

## 详细要求

### backend/app/schemas/user.py
- `UserCreate`：username(str 3-50), email(str email格式), password(str 6-20)
- `UserResponse`：id, username, email, created_at
- 使用 Pydantic v2 的 field_validator

### backend/app/routers/auth.py
- `POST /api/auth/register`
- 检查用户名是否已存在
- 检查邮箱是否已存在
- 使用 bcrypt 加密密码
- 创建用户记录
- 返回 UserResponse

### backend/tests/test_auth_register.py
使用 httpx AsyncClient 测试：
- 正常注册返回 201
- 用户名已存在返回 400
- 邮箱已存在返回 400
- 用户名过短返回 422
- 密码过短返回 422
- 邮箱格式错误返回 422

## 验收标准
1. `POST /api/auth/register` 接口可在 Swagger UI 中看到
2. 发送合法注册请求返回 201 和用户信息
3. 重复用户名返回 400 错误
4. 重复邮箱返回 400 错误
5. 参数验证失败返回 422
6. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_auth_register.py -v

# 手动测试
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"123456"}'
# 预期：201, {"code":0,"data":{"id":1,"username":"testuser",...},"message":"注册成功"}
```
