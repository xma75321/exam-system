"""认证相关 Pydantic 模型"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """用户注册请求"""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名（3-50 个字符）",
    )
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(
        ...,
        min_length=6,
        max_length=20,
        description="密码（6-20 个字符）",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """用户名只允许字母、数字和下划线"""
        if not v.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v


class UserLogin(BaseModel):
    """用户登录请求"""

    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """登录令牌响应"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """用户信息响应"""

    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
