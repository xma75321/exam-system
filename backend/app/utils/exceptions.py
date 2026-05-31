"""全局异常处理"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# ────────── 自定义异常类 ──────────


class AppException(Exception):
    """应用基础异常"""

    def __init__(self, code: int = 500, message: str = "服务器内部错误"):
        self.code = code
        self.message = message
        super().__init__(message)


class NotFoundException(AppException):
    """资源不存在"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=404, message=message)


class BadRequestException(AppException):
    """请求错误"""

    def __init__(self, message: str = "请求参数错误"):
        super().__init__(code=400, message=message)


class UnauthorizedException(AppException):
    """未认证"""

    def __init__(self, message: str = "未认证"):
        super().__init__(code=401, message=message)


class ForbiddenException(AppException):
    """无权限"""

    def __init__(self, message: str = "无权限"):
        super().__init__(code=403, message=message)


# ────────── 异常处理器 ──────────


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """处理自定义应用异常。"""
        logger.warning(
            "应用异常: %s %s -> %d: %s",
            request.method,
            request.url.path,
            exc.code,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "data": None,
                "message": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """处理未捕获的异常。"""
        logger.error(
            "未处理的异常: %s %s -> %s: %s",
            request.method,
            request.url.path,
            type(exc).__name__,
            str(exc),
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "data": None,
                "message": "服务器内部错误，请稍后重试",
            },
        )
