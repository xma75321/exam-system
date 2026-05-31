"""文件存储服务 — 处理上传文件的保存与验证"""

import os
import uuid

from fastapi import HTTPException, UploadFile

from app.config import settings

# .docx 文件魔数（PK zip 格式的前 4 字节）
DOCX_MAGIC = b"PK\x03\x04"


def save_upload(file: UploadFile) -> dict:
    """保存上传的文件到磁盘。

    Args:
        file: FastAPI UploadFile 对象

    Returns:
        包含 filename（原始文件名）、file_path（存储路径）、file_size 的字典

    Raises:
        HTTPException: 文件格式不支持或读取失败
    """
    # 验证扩展名
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail={
                "code": 2001,
                "message": "仅支持 .docx 格式文件",
            },
        )

    # 检查文件大小（先读取文件内容）
    content = file.file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail={
                "code": 2002,
                "message": f"文件大小不能超过 {settings.MAX_FILE_SIZE // (1024 * 1024)}MB",
            },
        )

    # 验证文件头（.docx 是 ZIP 格式，前 4 字节为 PK\x03\x04）
    if not content.startswith(DOCX_MAGIC):
        raise HTTPException(
            status_code=400,
            detail={
                "code": 2001,
                "message": "文件格式不支持，请上传有效的 .docx 文件",
            },
        )

    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "filename": file.filename,
        "file_path": file_path,
        "file_size": len(content),
    }
