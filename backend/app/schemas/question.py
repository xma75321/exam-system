"""题目入库请求/响应模型"""

from pydantic import BaseModel, Field


class OptionSaveItem(BaseModel):
    """选项入库项"""
    label: str
    content: str


class QuestionSaveItem(BaseModel):
    """题目入库项"""
    temp_id: str = ""
    type: str = Field(..., description="single | multi | judge | fill | essay")
    content: str
    options: list[OptionSaveItem] = []
    answer: str = ""
    score: float = 0.0
    explanation: str = ""


class QuestionSaveRequest(BaseModel):
    """确认入库请求"""
    filename: str = Field(..., description="原始文件名")
    questions: list[QuestionSaveItem] = Field(..., description="解析后的题目列表")


class QuestionResponse(BaseModel):
    """题目响应"""
    id: int
    type: str
    content: str
    answer: str
    score: float
    explanation: str

    model_config = {"from_attributes": True}


class QuestionSaveResponse(BaseModel):
    """入库响应"""
    exam_id: int
    questions: list[QuestionResponse]


class QuestionListItem(BaseModel):
    """题目列表项"""
    id: int
    type: str
    content: str
    score: float

    model_config = {"from_attributes": True}


class QuestionDetail(BaseModel):
    """题目详情（含选项）"""
    id: int
    type: str
    content: str
    options: list[OptionSaveItem] = []
    answer: str
    score: float
    explanation: str = ""

    model_config = {"from_attributes": True}


class QuestionListResponse(BaseModel):
    """题目列表分页响应"""
    items: list[QuestionListItem]
    total: int
    page: int
    page_size: int
