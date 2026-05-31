"""
数据库连接管理，使用 SQLAlchemy 2.0 风格。
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from app.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类，所有模型继承此类。"""
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入：获取数据库会话，请求结束后自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
