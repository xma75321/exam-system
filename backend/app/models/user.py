"""User 模型 — 用户账号信息"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户 ID")
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    created_at = Column(
        DateTime, server_default=func.now(), nullable=False, comment="注册时间"
    )
