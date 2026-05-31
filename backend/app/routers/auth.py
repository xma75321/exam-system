"""认证相关 API 路由"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=dict,
    status_code=201,
    summary="用户注册",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """注册新用户，检查用户名和邮箱唯一性，密码 bcrypt 加密存储。"""
    logger.info("注册请求: username=%s, email=%s", user_data.username, user_data.email)

    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        logger.warning("注册失败: 用户名 %s 已存在", user_data.username)
        raise HTTPException(
            status_code=400,
            detail={
                "code": 1001,
                "message": "用户名已被注册",
            },
        )

    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        logger.warning("注册失败: 邮箱 %s 已存在", user_data.email)
        raise HTTPException(
            status_code=400,
            detail={
                "code": 1001,
                "message": "邮箱已被注册",
            },
        )

    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("注册成功: user_id=%d, username=%s", user.id, user.username)

    logger.info("注册成功: user_id=%d", user.id)
    return {
        "code": 0,
        "data": UserResponse.model_validate(user).model_dump(),
        "message": "注册成功",
    }


@router.post(
    "/login",
    response_model=dict,
    summary="用户登录",
)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户名 + 密码登录，返回 JWT access token。"""
    logger.info("登录请求: username=%s", login_data.username)

    # 查找用户（支持用户名或邮箱登录）
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()

    if user is None:
        logger.warning("登录失败: 用户 %s 不存在", login_data.username)
        raise HTTPException(
            status_code=401,
            detail={
                "code": 1003,
                "message": "用户名或密码错误",
            },
        )

    if not verify_password(login_data.password, user.password_hash):
        logger.warning("登录失败: 用户 %s 密码错误", login_data.username)
        raise HTTPException(
            status_code=401,
            detail={
                "code": 1003,
                "message": "用户名或密码错误",
            },
        )

    # 创建 Token
    access_token = create_access_token(data={"sub": str(user.id)})
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 转换为秒

    logger.info("登录成功: user_id=%d", user.id)
    return {
        "code": 0,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expires_in,
        },
        "message": "登录成功",
    }


@router.get(
    "/me",
    response_model=dict,
    summary="获取当前用户",
)
def get_me(current_user: User = Depends(get_current_user)):
    """通过 JWT Token 获取当前登录用户的信息。"""
    return {
        "code": 0,
        "data": UserResponse.model_validate(current_user).model_dump(),
        "message": "success",
    }
