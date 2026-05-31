"""统计分析 API 路由"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.exam import Exam
from app.models.attempt import ExamAttempt
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/reports", tags=["统计"])


@router.get(
    "/overview",
    response_model=dict,
    summary="统计概览",
)
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户的考试统计概览。"""
    # 查询该用户的所有已完成考试
    attempts = (
        db.query(ExamAttempt)
        .filter(
            ExamAttempt.user_id == current_user.id,
            ExamAttempt.status == "graded",
            ExamAttempt.total_score.isnot(None),
        )
        .all()
    )

    if not attempts:
        return {
            "code": 0,
            "data": {
                "total_attempts": 0,
                "average_score": 0,
                "max_score": 0,
                "pass_rate": 0,
            },
            "message": "success",
        }

    total_attempts = len(attempts)
    scores = [float(a.total_score) for a in attempts if a.total_score is not None]
    average_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0

    # 计算通过率（需要关联考试获取 pass_score）
    passed_count = 0
    for attempt in attempts:
        exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
        if exam and attempt.total_score is not None and float(attempt.total_score) >= float(exam.pass_score):
            passed_count += 1

    pass_rate = (passed_count / total_attempts * 100) if total_attempts > 0 else 0

    return {
        "code": 0,
        "data": {
            "total_attempts": total_attempts,
            "average_score": round(average_score, 1),
            "max_score": round(max_score, 1),
            "pass_rate": round(pass_rate, 1),
        },
        "message": "success",
    }


@router.get(
    "/trend",
    response_model=dict,
    summary="成绩趋势",
)
def get_trend(
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取最近 N 天的成绩趋势。"""
    # 计算起始日期
    start_date = datetime.now() - timedelta(days=days)

    # 查询该时间段内的所有已完成考试
    attempts = (
        db.query(ExamAttempt)
        .filter(
            ExamAttempt.user_id == current_user.id,
            ExamAttempt.status == "graded",
            ExamAttempt.total_score.isnot(None),
            ExamAttempt.submitted_at >= start_date,
        )
        .order_by(ExamAttempt.submitted_at.asc())
        .all()
    )

    # 构建趋势数据
    trend_data = []
    for attempt in attempts:
        exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
        trend_data.append({
            "date": attempt.submitted_at.strftime("%Y-%m-%d") if attempt.submitted_at else None,
            "score": float(attempt.total_score) if attempt.total_score else 0,
            "exam_title": exam.title if exam else "未知考试",
            "pass_score": float(exam.pass_score) if exam else 60,
        })

    return {
        "code": 0,
        "data": trend_data,
        "message": "success",
    }
