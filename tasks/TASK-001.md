# TASK-001：后端项目初始化

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：4 小时
- **依赖**：无
- **前置条件**：无

## 任务描述
初始化 FastAPI 后端项目，配置基础结构、依赖和数据库连接。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/requirements.txt` | 创建 | Python 依赖清单 |
| 2 | `backend/app/__init__.py` | 创建 | 包初始化 |
| 3 | `backend/app/main.py` | 创建 | FastAPI 应用入口 |
| 4 | `backend/app/config.py` | 创建 | 配置管理（环境变量） |
| 5 | `backend/app/database.py` | 创建 | SQLAlchemy 数据库连接 |

## 详细要求

### backend/requirements.txt
包含以下依赖：
- fastapi
- uvicorn[standard]
- sqlalchemy
- pymysql
- alembic
- python-jose[cryptography]（JWT）
- passlib[bcrypt]（密码加密）
- python-multipart（文件上传）
- python-docx（Word 解析）
- pydantic
- pydantic-settings
- python-dotenv
- pytest
- httpx（测试客户端）

### backend/app/main.py
- 创建 FastAPI 实例
- 配置 CORS 中间件（允许前端地址）
- 注册路由（预留 `/api/auth`、`/api/upload`、`/api/questions`、`/api/exams`、`/api/attempts`、`/api/reports`）
- 添加健康检查端点 `GET /health`

### backend/app/config.py
- 使用 pydantic-settings 的 BaseSettings
- 从 `.env` 文件加载配置
- 配置项：DATABASE_URL、SECRET_KEY、ACCESS_TOKEN_EXPIRE_MINUTES、UPLOAD_DIR、MAX_FILE_SIZE、CORS_ORIGINS

### backend/app/database.py
- 使用 SQLAlchemy 2.0 风格
- 创建 engine、SessionLocal、Base
- 提供 `get_db` 依赖注入函数

## 验收标准
1. 运行 `pip install -r requirements.txt` 无报错
2. 运行 `uvicorn app.main:app --reload --port 8000` 成功启动
3. 访问 `http://localhost:8000/health` 返回 `{"status": "ok"}`
4. 访问 `http://localhost:8000/docs` 可看到 Swagger UI
5. 数据库连接配置可从环境变量读取

## 测试方法
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# 另一个终端
curl http://localhost:8000/health
# 预期：{"status": "ok"}
```
