"""JWT Token 和密码加密工具"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

# ────────── 常量 ──────────

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ────────── 密码工具 ──────────


def get_password_hash(password: str) -> str:
    """对密码进行 bcrypt 加密"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希值是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


# ────────── JWT 工具 ──────────


def create_access_token(data: dict) -> str:
    """创建 JWT access token。

    Args:
        data: 要编码到 Token 中的 payload 数据（如 {"sub": user_id}）

    Returns:
        JWT Token 字符串
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """验证并解析 JWT Token。

    Args:
        token: JWT Token 字符串

    Returns:
        解析后的 payload 字典

    Raises:
        HTTPException: Token 无效或已过期
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail={"code": 1004, "message": "Token 无效或已过期"},
        )


# ────────── 认证依赖 ──────────

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI 依赖：从请求头解析 JWT Token 并返回当前用户。

    Raises:
        HTTPException: 未提供 Token（401）或 Token 无效
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={"code": 1002, "message": "未提供认证 Token"},
        )

    payload = verify_token(credentials.credentials)
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail={"code": 1004, "message": "Token 无效"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail={"code": 1004, "message": "用户不存在"},
        )

    return user
