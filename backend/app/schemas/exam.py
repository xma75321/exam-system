"""考试请求/响应模型"""

from datetime import datetime

from pydantic import BaseModel, Field


class ExamCreate(BaseModel):
    """创建考试请求"""
    title: str = Field(..., min_length=1, max_length=200, description="考试标题")
    description: str = Field("", description="考试描述")
    duration_minutes: int = Field(..., ge=1, le=480, description="考试时长（分钟）")
    total_score: float = Field(..., ge=0, description="满分")
    pass_score: float = Field(..., ge=0, description="及格分")
    question_ids: list[int] = Field(..., min_length=1, description="题目 ID 列表")


class ExamUpdate(BaseModel):
    """更新考试请求（所有字段可选）"""
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    duration_minutes: int | None = Field(None, ge=1, le=480)
    total_score: float | None = Field(None, ge=0)
    pass_score: float | None = Field(None, ge=0)


class ExamListItem(BaseModel):
    """考试列表项"""
    id: int
    title: str
    description: str | None = None
    duration_minutes: int
    total_score: float
    pass_score: float
    status: str
    question_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ExamQuestionItem(BaseModel):
    """考试中的题目"""
    id: int
    type: str
    content: str
    score: float

    model_config = {"from_attributes": True}
