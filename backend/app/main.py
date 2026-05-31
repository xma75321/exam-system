"""
FastAPI 应用入口，配置 CORS 中间件并注册路由。
"""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import setup_logging
from app.utils.exceptions import register_exception_handlers

# 初始化日志
setup_logging()
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="智能考试系统 API",
    description="智能考试系统 MVP 版本 — 上传 Word 试卷 → 在线考试 → 自动评分",
    version="0.1.0",
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册全局异常处理器
register_exception_handlers(app)


# ────────── 请求日志中间件 ──────────

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录每个请求的处理时间和状态码。"""
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000

    # 只记录 API 请求，忽略静态文件
    if request.url.path.startswith("/api"):
        logger.info(
            "%s %s -> %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

    return response

# ────────── 健康检查 ──────────

@app.get("/health")
def health_check():
    """健康检查端点，用于确认服务正常运行。"""
    return {"status": "ok"}

# ────────── 路由注册 ──────────
from app.routers import auth as auth_router
from app.routers import upload as upload_router
from app.routers import questions as question_router
from app.routers import exams as exam_router
from app.routers import attempts as attempt_router
from app.routers import grade as grade_router
from app.routers import reports as reports_router

app.include_router(auth_router.router)
app.include_router(upload_router.router)
app.include_router(question_router.router)
app.include_router(exam_router.router)
app.include_router(attempt_router.router)
app.include_router(grade_router.router)
app.include_router(reports_router.router)
