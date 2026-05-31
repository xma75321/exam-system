"""评分 API 路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.attempt import ExamAttempt, QuestionResponse
from app.schemas.grade import ManualGradeRequest
from app.services.grade_service import grade_attempt, manual_grade
from app.utils.security import get_current_user

router = APIRouter(prefix="/api", tags=["评分"])


@router.post(
    "/attempts/{attempt_id}/grade",
    response_model=dict,
    summary="手动触发评分",
)
def trigger_grade(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """手动触发评分（通常由提交 API 自动调用）。"""
    # 验证作答记录存在
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "作答记录不存在"},
        )

    # 验证权限（只有本人可以触发评分）
    if attempt.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": 403, "message": "无权操作此作答记录"},
        )

    try:
        attempt = grade_attempt(db, attempt_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": 1001, "message": str(e)},
        )

    return {
        "code": 0,
        "data": {
            "id": attempt.id,
            "status": attempt.status,
            "total_score": float(attempt.total_score) if attempt.total_score else None,
            "objective_score": float(attempt.objective_score) if attempt.objective_score else None,
        },
        "message": "评分完成",
    }


@router.put(
    "/responses/{response_id}/score",
    response_model=dict,
    summary="手动评分简答题",
)
def grade_response(
    response_id: int,
    body: ManualGradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """手动评分简答题。"""
    try:
        response = manual_grade(
            db,
            response_id,
            body.score,
            current_user.id,
            body.comment,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": 1001, "message": str(e)},
        )

    # 获取 attempt 信息
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == response.attempt_id).first()

    return {
        "code": 0,
        "data": {
            "response_id": response.id,
            "score": float(response.score) if response.score else None,
            "graded_by": response.graded_by,
            "attempt_status": attempt.status if attempt else None,
            "total_score": float(attempt.total_score) if attempt and attempt.total_score else None,
        },
        "message": "评分成功",
    }
