"""
应用配置管理，使用 pydantic-settings 从环境变量和 .env 文件加载配置。
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用全局配置"""

    # 数据库
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/exam_system"

    # JWT 认证
    SECRET_KEY: str = "exam-system-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 小时

    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
