# TASK-006：前端认证页面

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：6 小时
- **依赖**：TASK-002, TASK-005
- **前置条件**：前后端项目初始化完成，登录 API 可用

## 任务描述
实现前端注册和登录页面，包括表单验证、API 对接和认证状态管理。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/app/auth/page.tsx` | 创建 | 注册/登录页面 |
| 2 | `frontend/src/hooks/useAuth.ts` | 创建 | 认证状态 Hook |
| 3 | `frontend/src/lib/api.ts` | 创建 | API 客户端封装 |
| 4 | `frontend/src/types/auth.ts` | 创建 | 认证相关类型定义 |
| 5 | `frontend/src/components/Toast.tsx` | 创建 | 通知提示组件 |

## 详细要求

### frontend/src/lib/api.ts
- 封装 fetch 请求
- 自动添加 Authorization header（从 localStorage 读取 Token）
- 统一错误处理（401 跳转登录）
- 导出 `authApi` 对象（register, login, me 方法）

### frontend/src/types/auth.ts
- `User`：id, username, email, created_at
- `LoginRequest`：username, password
- `RegisterRequest`：username, email, password
- `TokenResponse`：access_token, token_type, expires_in
- `ApiResponse<T>`：code, data, message

### frontend/src/hooks/useAuth.ts
- 使用 Zustand 管理认证状态
- 状态：user, token, isLoading
- 方法：login, register, logout, checkAuth
- Token 持久化到 localStorage
- 自动检查 Token 有效性

### frontend/src/app/auth/page.tsx
- Tab 切换：登录 / 注册
- 登录表单：用户名 + 密码 + 提交按钮
- 注册表单：用户名 + 邮箱 + 密码 + 确认密码 + 提交按钮
- 使用 react-hook-form + zod 验证
- 提交成功后跳转 /dashboard
- 错误提示使用 Toast 组件

### frontend/src/components/Toast.tsx
- 支持 success/error/info 类型
- 自动消失（3 秒）
- 使用 React Portal 渲染

## 验收标准
1. 浏览器访问 `/auth` 显示登录/注册页面
2. 注册表单验证正常（用户名长度、邮箱格式、密码匹配）
3. 注册成功后自动切换到登录 Tab
4. 登录成功后跳转到 `/dashboard`
5. Token 存储在 localStorage
6. 刷新页面后保持登录状态
7. 登出后清除 Token 并跳转到 `/auth`

## 测试方法
```bash
cd frontend
npm run dev
# 1. 访问 http://localhost:3000/auth
# 2. 注册一个新用户
# 3. 使用新用户登录
# 4. 验证跳转到 /dashboard
# 5. 刷新页面，验证仍处于登录状态
```
