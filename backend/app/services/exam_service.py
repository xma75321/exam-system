"""考试管理服务"""

import logging

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.exam import Exam, Question
from app.schemas.exam import ExamCreate, ExamUpdate

logger = logging.getLogger(__name__)


def create_exam(
    db: Session,
    data: ExamCreate,
    user_id: int,
) -> Exam:
    """创建考试并关联题目。

    将选中的题目从其原所属考试移至新创建的考试。

    Raises:
        ValueError: question_ids 中有不存在的 ID
    """
    # 验证题目是否存在
    existing_count = (
        db.query(func.count(Question.id))
        .filter(Question.id.in_(data.question_ids))
        .scalar()
    )
    if existing_count != len(data.question_ids):
        raise ValueError("部分题目 ID 不存在")

    # 创建考试
    exam = Exam(
        title=data.title,
        description=data.description or "",
        duration_minutes=data.duration_minutes,
        total_score=data.total_score,
        pass_score=data.pass_score,
        status="draft",
        created_by=user_id,
    )
    db.add(exam)
    db.flush()

    # 将题目关联到新考试
    questions = (
        db.query(Question)
        .filter(Question.id.in_(data.question_ids))
        .all()
    )
    for idx, question in enumerate(questions):
        question.exam_id = exam.id
        question.sort_order = idx + 1

    db.commit()
    db.refresh(exam)
    return exam


def list_exams(
    db: Session,
    user_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple:
    """分页查询考试列表。"""
    query = db.query(Exam)
    if user_id:
        query = query.filter(Exam.created_by == user_id)
    if status:
        query = query.filter(Exam.status == status)

    total = query.count()
    items = (
        query.order_by(Exam.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_exam(db: Session, exam_id: int) -> Exam | None:
    """获取考试详情。"""
    return db.query(Exam).filter(Exam.id == exam_id).first()


def update_exam(
    db: Session,
    exam_id: int,
    data: ExamUpdate,
) -> Exam | None:
    """更新考试配置。"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(exam, key, value)

    db.commit()
    db.refresh(exam)
    return exam


def delete_exam(db: Session, exam_id: int) -> bool:
    """删除考试（级联删除关联题目和选项）。"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        return False
    db.delete(exam)
    db.commit()
    return True


def publish_exam(db: Session, exam_id: int) -> Exam | None:
    """发布考试（draft → open），需至少包含 1 题。"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        return None

    question_count = (
        db.query(func.count(Question.id))
        .filter(Question.exam_id == exam_id)
        .scalar()
    )
    if question_count == 0:
        raise ValueError("考试至少需要包含 1 道题目才能发布")

    exam.status = "open"
    db.commit()
    db.refresh(exam)
    return exam


def close_exam(db: Session, exam_id: int) -> Exam | None:
    """关闭考试（open → closed）。"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        return None

    exam.status = "closed"
    db.commit()
    db.refresh(exam)
    return exam
