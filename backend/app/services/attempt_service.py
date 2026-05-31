"""答题服务"""

import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.exam import Exam, Question, Option
from app.models.attempt import ExamAttempt, QuestionResponse
from app.models.user import User

logger = logging.getLogger(__name__)


def start_exam(
    db: Session,
    exam_id: int,
    user_id: int,
) -> ExamAttempt:
    """开始考试。

    创建作答记录和所有题目的 response 记录。
    如果有未完成的作答记录，则返回该记录（继续答题）。
    如果有已完成的作答记录，允许重新考试。

    Raises:
        ValueError: 考试不存在、考试未开放
    """
    # 验证考试
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        raise ValueError("考试不存在")

    if exam.status != "open":
        raise ValueError("考试未开放，无法参加")

    # 检查是否有未完成的作答记录
    in_progress = (
        db.query(ExamAttempt)
        .filter(
            ExamAttempt.exam_id == exam_id,
            ExamAttempt.user_id == user_id,
            ExamAttempt.status == "in_progress",
        )
        .first()
    )
    if in_progress is not None:
        # 返回未完成的作答记录，继续答题
        return in_progress

    # 创建新的作答记录（允许重新考试）
    attempt = ExamAttempt(
        exam_id=exam_id,
        user_id=user_id,
        status="in_progress",
    )
    db.add(attempt)
    db.flush()

    # 为每道题创建 response 记录
    questions = (
        db.query(Question)
        .filter(Question.exam_id == exam_id)
        .order_by(Question.sort_order)
        .all()
    )
    for question in questions:
        response = QuestionResponse(
            attempt_id=attempt.id,
            question_id=question.id,
            user_answer=None,
            graded_by="pending",
        )
        db.add(response)

    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(
    db: Session,
    attempt_id: int,
) -> tuple[ExamAttempt, Exam, list[Question], dict[int, str | None]] | None:
    """获取作答进度。

    Returns:
        (attempt, exam, questions, answers_map) 或 None
    """
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        return None

    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    if exam is None:
        return None

    questions = (
        db.query(Question)
        .filter(Question.exam_id == attempt.exam_id)
        .order_by(Question.sort_order)
        .all()
    )

    # 获取已保存的答案
    responses = (
        db.query(QuestionResponse)
        .filter(QuestionResponse.attempt_id == attempt_id)
        .all()
    )
    answers_map: dict[int, str | None] = {
        r.question_id: r.user_answer for r in responses
    }

    return attempt, exam, questions, answers_map


def save_answers(
    db: Session,
    attempt_id: int,
    answers: list[dict],
) -> None:
    """保存答案。

    Raises:
        ValueError: 作答记录不存在、状态不正确、已超时
    """
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        raise ValueError("作答记录不存在")

    if attempt.status != "in_progress":
        raise ValueError("考试已提交，无法保存答案")

    # 检查是否超时
    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    if exam is None:
        raise ValueError("考试不存在")

    end_time = attempt.started_at + timedelta(minutes=exam.duration_minutes)
    if datetime.utcnow() > end_time:
        raise ValueError("考试已超时，无法保存答案")

    # 更新答案
    for answer in answers:
        response = (
            db.query(QuestionResponse)
            .filter(
                QuestionResponse.attempt_id == attempt_id,
                QuestionResponse.question_id == answer["question_id"],
            )
            .first()
        )
        if response is not None:
            response.user_answer = answer["user_answer"]

    db.commit()


def submit_exam(
    db: Session,
    attempt_id: int,
) -> ExamAttempt:
    """提交考试并自动评分。

    Raises:
        ValueError: 作答记录不存在、状态不正确
    """
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        raise ValueError("作答记录不存在")

    if attempt.status != "in_progress":
        raise ValueError("考试已提交，不能重复提交")

    attempt.status = "submitted"
    attempt.submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(attempt)

    # 自动评分
    from app.services.grade_service import grade_attempt
    try:
        attempt = grade_attempt(db, attempt_id)
    except Exception as e:
        # 评分失败不影响提交
        logger.warning(f"自动评分失败: {e}")

    return attempt


def get_question_with_options(
    db: Session,
    question_id: int,
) -> tuple[Question, list[Option]]:
    """获取题目和选项。"""
    question = db.query(Question).filter(Question.id == question_id).first()
    options = (
        db.query(Option)
        .filter(Option.question_id == question_id)
        .order_by(Option.id)
        .all()
    )
    return question, options
