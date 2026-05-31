"""评分请求/响应模型"""

from pydantic import BaseModel, Field


class ManualGradeRequest(BaseModel):
    """手动评分请求"""
    score: float = Field(..., ge=0, description="得分")
    comment: str | None = Field(None, description="评语")


class GradeResult(BaseModel):
    """评分结果"""
    total_score: float | None = None
    objective_score: float | None = None
    subjective_score: float | None = None
    correct_count: int = 0
    total_count: int = 0
