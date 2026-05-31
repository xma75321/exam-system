"""考试管理 API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.exam import Question
from app.schemas.exam import ExamCreate, ExamUpdate
from app.services.exam_service import (
    create_exam,
    list_exams,
    get_exam,
    update_exam,
    delete_exam,
    publish_exam,
    close_exam,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/exams", tags=["考试管理"])


@router.post(
    "",
    response_model=dict,
    status_code=201,
    summary="创建考试",
)
def create(
    body: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """从题库中选择题目创建考试。"""
    try:
        exam = create_exam(db, body, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": 1001, "message": str(e)},
        )

    question_count = db.query(Question).filter(Question.exam_id == exam.id).count()

    return {
        "code": 0,
        "data": {
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "duration_minutes": exam.duration_minutes,
            "total_score": float(exam.total_score),
            "pass_score": float(exam.pass_score),
            "status": exam.status,
            "question_count": question_count,
            "created_at": exam.created_at.isoformat() if exam.created_at else "",
        },
        "message": "创建成功",
    }


@router.get(
    "",
    response_model=dict,
    summary="考试列表",
)
def list_all(
    status: str | None = Query(None, description="按状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """分页查询当前用户的考试列表。"""
    items, total = list_exams(db, user_id=current_user.id, status=status, page=page, page_size=page_size)

    exam_items = []
    for exam in items:
        question_count = db.query(Question).filter(Question.exam_id == exam.id).count()
        exam_items.append({
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "duration_minutes": exam.duration_minutes,
            "total_score": float(exam.total_score),
            "pass_score": float(exam.pass_score),
            "status": exam.status,
            "question_count": question_count,
            "created_at": exam.created_at.isoformat() if exam.created_at else "",
        })

    return {
        "code": 0,
        "data": {
            "items": exam_items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        "message": "success",
    }


@router.get(
    "/{exam_id}",
    response_model=dict,
    summary="考试详情",
)
def detail(
    exam_id: int,
    db: Session = Depends(get_db),
):
    """获取考试详情，含题目列表。"""
    exam = get_exam(db, exam_id)
    if exam is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "考试不存在"},
        )

    questions = (
        db.query(Question)
        .filter(Question.exam_id == exam_id)
        .order_by(Question.sort_order)
        .all()
    )

    return {
        "code": 0,
        "data": {
            "id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "duration_minutes": exam.duration_minutes,
            "total_score": float(exam.total_score),
            "pass_score": float(exam.pass_score),
            "status": exam.status,
            "question_count": len(questions),
            "questions": [
                {
                    "id": q.id,
                    "type": q.type,
                    "content": q.content,
                    "score": float(q.score),
                }
                for q in questions
            ],
            "created_at": exam.created_at.isoformat() if exam.created_at else "",
        },
        "message": "success",
    }


@router.put(
    "/{exam_id}",
    response_model=dict,
    summary="更新考试",
)
def update(
    exam_id: int,
    body: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新考试配置。"""
    exam = update_exam(db, exam_id, body)
    if exam is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "考试不存在"},
        )

    return {
        "code": 0,
        "data": {
            "id": exam.id,
            "title": exam.title,
        },
        "message": "更新成功",
    }


@router.delete(
    "/{exam_id}",
    response_model=dict,
    summary="删除考试",
)
def delete(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除考试（级联删除关联题目）。"""
    success = delete_exam(db, exam_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "考试不存在"},
        )

    return {
        "code": 0,
        "data": None,
        "message": "删除成功",
    }


@router.post(
    "/{exam_id}/publish",
    response_model=dict,
    summary="发布考试",
)
def publish(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发布考试（draft → open）。"""
    try:
        exam = publish_exam(db, exam_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": 1001, "message": str(e)},
        )

    if exam is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "考试不存在"},
        )

    return {
        "code": 0,
        "data": {"id": exam.id, "status": exam.status},
        "message": "发布成功",
    }


@router.post(
    "/{exam_id}/close",
    response_model=dict,
    summary="关闭考试",
)
def close(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """关闭考试（open → closed）。"""
    exam = close_exam(db, exam_id)
    if exam is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "考试不存在"},
        )

    return {
        "code": 0,
        "data": {"id": exam.id, "status": exam.status},
        "message": "已关闭",
    }
