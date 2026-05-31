"""答题请求/响应模型"""

from datetime import datetime
from pydantic import BaseModel, Field


class AttemptStart(BaseModel):
    """开始考试请求"""
    exam_id: int = Field(..., description="考试 ID")


class QuestionInAttempt(BaseModel):
    """考试中的题目（不含答案）"""
    id: int
    type: str
    content: str
    score: float
    sort_order: int
    options: list["OptionInAttempt"] | None = None


class OptionInAttempt(BaseModel):
    """题目选项（不含是否正确）"""
    id: int
    label: str
    content: str


class AttemptResponse(BaseModel):
    """开始考试/获取进度响应"""
    id: int
    exam_id: int
    exam_title: str
    status: str
    started_at: datetime
    duration_minutes: int
    end_time: datetime | None = None
    questions: list[QuestionInAttempt]


class AnswerItem(BaseModel):
    """单个答案"""
    question_id: int = Field(..., description="题目 ID")
    user_answer: str = Field(..., description="用户答案")


class AnswerSave(BaseModel):
    """保存答案请求"""
    answers: list[AnswerItem] = Field(..., min_length=1, description="答案列表")


class AnsweredQuestion(BaseModel):
    """已作答题目"""
    question_id: int
    user_answer: str | None = None


class AttemptProgressResponse(BaseModel):
    """答题进度响应"""
    id: int
    exam_id: int
    exam_title: str
    status: str
    started_at: datetime
    duration_minutes: int
    end_time: datetime | None = None
    questions: list[QuestionInAttempt]
    answered: list[AnsweredQuestion]


class QuestionResult(BaseModel):
    """题目结果（含正确答案和得分）"""
    id: int
    type: str
    content: str
    score: float
    sort_order: int
    options: list[OptionInAttempt] | None = None
    user_answer: str | None = None
    correct_answer: str
    earned_score: float | None = None
    is_correct: bool | None = None
    explanation: str | None = None


class TypeStat(BaseModel):
    """题型统计"""
    type: str
    total: int
    correct: int
    pending: int = 0


class AttemptResultResponse(BaseModel):
    """考试结果响应"""
    id: int
    exam_id: int
    exam_title: str
    status: str
    started_at: datetime
    submitted_at: datetime | None = None
    duration_minutes: int
    total_score: float | None = None
    objective_score: float | None = None
    subjective_score: float | None = None
    pass_score: float
    total_questions: int
    correct_count: int
    pending_count: int = 0
    is_passed: bool | None = None
    questions: list[QuestionResult]
    type_stats: list[TypeStat]
