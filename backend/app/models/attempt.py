"""ExamAttempt、QuestionResponse 模型 — 答题记录与作答"""

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    DateTime,
    Numeric,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ExamAttempt(Base):
    """考试作答记录表"""

    __tablename__ = "exam_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="作答记录 ID")
    exam_id = Column(
        Integer, ForeignKey("exams.id"), nullable=False, comment="考试 ID"
    )
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="用户 ID"
    )
    started_at = Column(
        DateTime, server_default=func.now(), nullable=False, comment="开始时间"
    )
    submitted_at = Column(DateTime, nullable=True, comment="提交时间")
    status = Column(
        Enum("in_progress", "submitted", "graded", name="attempt_status"),
        nullable=False,
        default="in_progress",
        comment="作答状态",
    )
    total_score = Column(Numeric(5, 1), nullable=True, comment="总分")
    objective_score = Column(Numeric(5, 1), nullable=True, comment="客观题得分")
    subjective_score = Column(Numeric(5, 1), nullable=True, comment="主观题得分")

    # 关系
    exam = relationship("Exam", backref="attempts")
    user = relationship("User", backref="attempts")
    responses = relationship(
        "QuestionResponse", back_populates="attempt", cascade="all, delete-orphan"
    )


class QuestionResponse(Base):
    """题目作答表"""

    __tablename__ = "question_responses"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="作答 ID")
    attempt_id = Column(
        Integer,
        ForeignKey("exam_attempts.id"),
        nullable=False,
        comment="作答记录 ID",
    )
    question_id = Column(
        Integer, ForeignKey("questions.id"), nullable=False, comment="题目 ID"
    )
    user_answer = Column(Text, nullable=True, comment="用户答案")
    is_correct = Column(Boolean, nullable=True, comment="是否正确")
    score = Column(Numeric(5, 1), nullable=True, comment="得分")
    graded_by = Column(
        Enum("auto", "manual", "pending", name="graded_by_type"),
        nullable=False,
        default="pending",
        comment="评分方式",
    )

    # 关系
    attempt = relationship("ExamAttempt", back_populates="responses")
    question = relationship("Question", backref="responses")
