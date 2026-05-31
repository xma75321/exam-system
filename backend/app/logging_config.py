"""
日志配置模块，统一管理后端日志格式和输出。
"""

import logging
import sys


def setup_logging() -> None:
    """配置应用日志格式和处理器。"""

    # 日志格式：时间 | 级别 | 模块 | 消息
    log_format = "%(asctime)s | %(levelname)-7s | %(module)s:%(funcName)s:%(lineno)d | %(message)s"
    date_format = "%H:%M:%S"

    # 配置根日志器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # 隐藏访问日志
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)  # 隐藏 SQL 日志

    logger = logging.getLogger(__name__)
    logger.info("日志系统已初始化")
