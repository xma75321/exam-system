"""题库管理 API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.exam import Option
from app.services.question_service import list_questions, get_question, delete_question
from app.schemas.question import QuestionListItem, QuestionDetail, OptionSaveItem
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/questions", tags=["题库管理"])


@router.get(
    "",
    response_model=dict,
    summary="题目列表",
)
def get_questions(
    q_type: str | None = Query(None, alias="type", description="题型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询当前用户上传的题目列表，支持按题型筛选。"""
    items, total = list_questions(db, user_id=current_user.id, q_type=q_type, page=page, page_size=page_size)

    question_items = [
        {
            "id": q.id,
            "type": q.type,
            "content": q.content[:100] if len(q.content) > 100 else q.content,
            "score": float(q.score),
        }
        for q in items
    ]

    return {
        "code": 0,
        "data": {
            "items": question_items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        "message": "success",
    }


@router.get(
    "/{question_id}",
    response_model=dict,
    summary="题目详情",
)
def get_question_detail(
    question_id: int,
    db: Session = Depends(get_db),
):
    """获取题目完整信息，包含选项、答案和解析。"""
    question = get_question(db, question_id)
    if question is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "题目不存在"},
        )

    options = [
        {"label": opt.label, "content": opt.content}
        for opt in question.options
    ]

    return {
        "code": 0,
        "data": {
            "id": question.id,
            "type": question.type,
            "content": question.content,
            "options": options,
            "answer": question.answer,
            "score": float(question.score),
            "explanation": question.explanation or "",
        },
        "message": "success",
    }


@router.delete(
    "/{question_id}",
    response_model=dict,
    summary="删除题目",
)
def remove_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除指定题目（需要认证）。"""
    success = delete_question(db, question_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "题目不存在"},
        )

    return {
        "code": 0,
        "data": None,
        "message": "删除成功",
    }
