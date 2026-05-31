"""评分服务"""

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.attempt import ExamAttempt, QuestionResponse
from app.models.exam import Question

logger = logging.getLogger(__name__)


def grade_attempt(db: Session, attempt_id: int) -> ExamAttempt:
    """对作答记录进行评分。

    自动评客观题，主观题标记为 pending。

    Raises:
        ValueError: 作答记录不存在、状态不正确
    """
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        raise ValueError("作答记录不存在")

    if attempt.status not in ("submitted", "graded"):
        raise ValueError("只能对已提交的考试进行评分")

    # 获取所有 response
    responses = (
        db.query(QuestionResponse)
        .filter(QuestionResponse.attempt_id == attempt_id)
        .all()
    )

    total_score = Decimal("0")
    objective_score = Decimal("0")

    for response in responses:
        question = db.query(Question).filter(Question.id == response.question_id).first()
        if question is None:
            continue

        # 按题型评分
        if question.type in ("single", "multi", "judge", "fill"):
            score = grade_objective(response, question)
            total_score += score
            objective_score += score
        elif question.type == "essay":
            grade_essay(response)

    # 更新 attempt
    attempt.total_score = total_score
    attempt.objective_score = objective_score
    attempt.status = "graded"

    db.commit()
    db.refresh(attempt)
    return attempt


def grade_objective(response: QuestionResponse, question: Question) -> Decimal:
    """评分客观题（单选、多选、判断、填空）。"""
    if response.user_answer is None or response.user_answer.strip() == "":
        response.is_correct = False
        response.score = Decimal("0")
        response.graded_by = "auto"
        return Decimal("0")

    correct_answer = question.answer.strip()
    user_answer = response.user_answer.strip()

    if question.type == "single":
        is_correct = grade_single_choice(user_answer, correct_answer)
    elif question.type == "multi":
        is_correct = grade_multi_choice(user_answer, correct_answer)
    elif question.type == "judge":
        is_correct = grade_judge(user_answer, correct_answer)
    elif question.type == "fill":
        is_correct = grade_fill(user_answer, correct_answer)
    else:
        is_correct = False

    response.is_correct = is_correct
    response.score = question.score if is_correct else Decimal("0")
    response.graded_by = "auto"

    return response.score


def grade_single_choice(user_answer: str, correct_answer: str) -> bool:
    """单选题评分：完全匹配。"""
    return user_answer == correct_answer


def grade_multi_choice(user_answer: str, correct_answer: str) -> bool:
    """多选题评分：完全匹配（全对才得分）。"""
    # 将答案转换为集合进行比较
    user_set = set(answer.strip() for answer in user_answer.split(",") if answer.strip())
    correct_set = set(answer.strip() for answer in correct_answer.split(",") if answer.strip())
    return user_set == correct_set


def grade_judge(user_answer: str, correct_answer: str) -> bool:
    """判断题评分：完全匹配。"""
    return user_answer == correct_answer


def grade_fill(user_answer: str, correct_answer: str) -> bool:
    """填空题评分：忽略大小写和首尾空格。"""
    # 多空题：按分号或逗号分隔
    user_parts = [p.strip().lower() for p in user_answer.replace("；", ";").split(";") if p.strip()]
    correct_parts = [p.strip().lower() for p in correct_answer.replace("；", ";").split(";") if p.strip()]

    if len(user_parts) != len(correct_parts):
        return False

    return all(u == c for u, c in zip(user_parts, correct_parts))


def grade_essay(response: QuestionResponse) -> None:
    """简答题评分：标记为 pending。"""
    response.is_correct = None
    response.score = None
    response.graded_by = "pending"


def manual_grade(
    db: Session,
    response_id: int,
    score: float,
    user_id: int,
    comment: str | None = None,
) -> QuestionResponse:
    """手动评分简答题。

    Raises:
        ValueError: response 不存在、非简答题、分值超限、无权限
    """
    response = db.query(QuestionResponse).filter(QuestionResponse.id == response_id).first()
    if response is None:
        raise ValueError("作答记录不存在")

    # 验证权限（通过 attempt 关联）
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == response.attempt_id).first()
    if attempt is None or attempt.user_id != user_id:
        raise ValueError("无权操作此作答记录")

    # 验证题目类型
    question = db.query(Question).filter(Question.id == response.question_id).first()
    if question is None:
        raise ValueError("题目不存在")
    if question.type != "essay":
        raise ValueError("只能手动评分简答题")

    # 验证分值
    if score < 0 or score > float(question.score):
        raise ValueError(f"分值必须在 0 到 {question.score} 之间")

    # 更新 response
    response.score = Decimal(str(score))
    response.is_correct = score > 0
    response.graded_by = "manual"

    # 重新计算 attempt 总分
    recalculate_attempt_scores(db, response.attempt_id)

    db.commit()
    db.refresh(response)
    return response


def recalculate_attempt_scores(db: Session, attempt_id: int) -> None:
    """重新计算 attempt 的总分。"""
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        return

    responses = (
        db.query(QuestionResponse)
        .filter(QuestionResponse.attempt_id == attempt_id)
        .all()
    )

    total_score = Decimal("0")
    objective_score = Decimal("0")
    subjective_score = Decimal("0")
    all_graded = True

    for response in responses:
        if response.score is not None:
            question = db.query(Question).filter(Question.id == response.question_id).first()
            if question and question.type in ("single", "multi", "judge", "fill"):
                objective_score += response.score
            else:
                subjective_score += response.score
            total_score += response.score
        else:
            all_graded = False

    attempt.total_score = total_score
    attempt.objective_score = objective_score
    attempt.subjective_score = subjective_score

    # 如果所有题目都已评分，更新状态
    if all_graded:
        attempt.status = "graded"
