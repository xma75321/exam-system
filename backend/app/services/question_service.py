"""题目入库服务 — 将解析结果保存到数据库"""

import logging

from sqlalchemy.orm import Session

from app.models.exam import Exam, Question, Option
from app.schemas.question import QuestionSaveItem, QuestionResponse

logger = logging.getLogger(__name__)


def save_questions(
    db: Session,
    filename: str,
    questions: list[QuestionSaveItem],
    user_id: int,
) -> dict:
    """将用户确认的解析结果批量入库。

    Args:
        db: 数据库会话
        filename: 原始文件名
        questions: 解析后的题目列表
        user_id: 当前登录用户 ID

    Returns:
        {"exam_id": int, "questions": list[QuestionResponse]}
    """
    # 创建考试记录（草稿状态）
    exam = Exam(
        title=filename,
        description=f"从 {filename} 导入的试卷",
        duration_minutes=60,  # 默认时长，后续可修改
        total_score=sum(q.score for q in questions),
        pass_score=sum(q.score for q in questions) * 0.6,  # 默认 60% 及格
        status="draft",
        created_by=user_id,
    )
    db.add(exam)
    db.flush()  # 获取 exam.id

    saved_questions: list[QuestionResponse] = []
    for idx, item in enumerate(questions, start=1):
        question = Question(
            exam_id=exam.id,
            type=item.type,
            content=item.content,
            answer=item.answer,
            score=item.score,
            explanation=item.explanation or "",
            sort_order=idx,
        )
        db.add(question)
        db.flush()  # 获取 question.id

        # 保存选项（仅选择题）
        if item.options:
            for opt in item.options:
                is_correct = opt.label.upper() in item.answer.upper().replace(" ", "").split(",")
                option = Option(
                    question_id=question.id,
                    label=opt.label.upper(),
                    content=opt.content,
                    is_correct=is_correct,
                )
                db.add(option)

        saved_questions.append(
            QuestionResponse(
                id=question.id,
                type=question.type,
                content=question.content,
                answer=question.answer,
                score=float(question.score),
                explanation=question.explanation or "",
            )
        )

    db.commit()
    return {
        "exam_id": exam.id,
        "questions": saved_questions,
    }


def list_questions(
    db: Session,
    user_id: int | None = None,
    q_type: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple:
    """分页查询题目列表。

    Args:
        db: 数据库会话
        user_id: 用户ID筛选（可选，只返回该用户上传的题目）
        q_type: 题型筛选（可选）
        page: 页码（从 1 开始）
        page_size: 每页条数

    Returns:
        (items: list[Question], total: int)
    """
    query = db.query(Question)
    if user_id:
        # 只返回该用户创建的考试中的题目
        query = query.join(Exam, Question.exam_id == Exam.id).filter(Exam.created_by == user_id)
    if q_type:
        query = query.filter(Question.type == q_type)

    total = query.count()
    items = (
        query.order_by(Question.sort_order.desc(), Question.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total


def get_question(db: Session, question_id: int) -> Question | None:
    """获取单个题目详情（含选项）。"""
    return db.query(Question).filter(Question.id == question_id).first()


def delete_question(db: Session, question_id: int) -> bool:
    """删除题目（级联删除选项）。"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        return False
    db.delete(question)
    db.commit()
    return True
