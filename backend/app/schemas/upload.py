"""上传相关 Pydantic 模型"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """文件上传成功响应"""
    filename: str
    file_path: str
    file_size: int
    total_count: int = 0
    questions: list = []
