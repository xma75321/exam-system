"""Exam、Question、Option 模型 — 考试与题库"""

from sqlalchemy import (
    Column,
    Integer,
    String,
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


class Exam(Base):
    """考试表"""

    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="考试 ID")
    title = Column(String(200), nullable=False, comment="考试标题")
    description = Column(Text, nullable=True, comment="考试描述")
    duration_minutes = Column(Integer, nullable=False, comment="考试时长（分钟）")
    total_score = Column(
        Numeric(5, 1), nullable=False, comment="满分"
    )
    pass_score = Column(
        Numeric(5, 1), nullable=False, comment="及格分"
    )
    status = Column(
        Enum("draft", "open", "closed", name="exam_status"),
        nullable=False,
        default="draft",
        comment="考试状态",
    )
    created_by = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="创建者 ID"
    )
    created_at = Column(
        DateTime, server_default=func.now(), nullable=False, comment="创建时间"
    )

    # 关系
    questions = relationship(
        "Question", back_populates="exam", cascade="all, delete-orphan"
    )
    creator = relationship("User", backref="exams")


class Question(Base):
    """题目表"""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="题目 ID")
    exam_id = Column(
        Integer, ForeignKey("exams.id"), nullable=False, comment="所属考试 ID"
    )
    type = Column(
        Enum("single", "multi", "judge", "fill", "essay", name="question_type"),
        nullable=False,
        comment="题型",
    )
    content = Column(Text, nullable=False, comment="题目内容")
    answer = Column(Text, nullable=False, comment="正确答案")
    score = Column(
        Numeric(5, 1), nullable=False, comment="分值"
    )
    explanation = Column(Text, nullable=True, comment="题目解析")
    sort_order = Column(
        Integer, nullable=False, default=0, comment="排序序号"
    )

    # 关系
    exam = relationship("Exam", back_populates="questions")
    options = relationship(
        "Option", back_populates="question", cascade="all, delete-orphan"
    )


class Option(Base):
    """选项表（用于单选、多选、判断题）"""

    __tablename__ = "options"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="选项 ID")
    question_id = Column(
        Integer, ForeignKey("questions.id"), nullable=False, comment="所属题目 ID"
    )
    label = Column(String(5), nullable=False, comment="选项标签（A/B/C/D 或 正确/错误）")
    content = Column(Text, nullable=False, comment="选项内容")
    is_correct = Column(
        Boolean, nullable=False, default=False, comment="是否为正确答案"
    )

    # 关系
    question = relationship("Question", back_populates="options")
