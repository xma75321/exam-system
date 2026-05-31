"""文件上传 API 路由"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.question import QuestionSaveRequest
from app.services.upload_service import save_upload
from app.services.word_parser import parse_word_document
from app.services.question_service import save_questions
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/upload", tags=["上传解析"])


@router.post(
    "",
    response_model=dict,
    summary="上传 Word 试卷",
)
def upload_file(file: UploadFile = File(...)):
    """上传 .docx 格式的 Word 试卷文件，验证格式并保存到服务器，
    并自动解析试卷内容返回结构化题目数据。
    """
    result = save_upload(file)
    parse_result = parse_word_document(result["file_path"])

    return {
        "code": 0,
        "data": {
            "filename": result["filename"],
            "file_path": result["file_path"],
            "file_size": result["file_size"],
            "total_count": parse_result.total_count,
            "questions": [q.model_dump() for q in parse_result.questions],
            "type_summary": parse_result.type_summary,
        },
        "message": "解析成功",
    }


@router.post(
    "/confirm",
    response_model=dict,
    status_code=201,
    summary="确认入库",
)
def confirm_upload(
    body: QuestionSaveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """将用户确认后的解析结果保存到题库。

    需要认证 Token，创建 exam 记录和关联的 questions/options。
    """
    result = save_questions(
        db=db,
        filename=body.filename,
        questions=body.questions,
        user_id=current_user.id,
    )

    return {
        "code": 0,
        "data": {
            "exam_id": result["exam_id"],
            "questions": [q.model_dump() for q in result["questions"]],
        },
        "message": "入库成功",
    }
