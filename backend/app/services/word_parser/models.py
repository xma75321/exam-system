"""Word 解析中间数据模型"""

from pydantic import BaseModel


class ParsedQuestion(BaseModel):
    """解析后的单个题目"""

    temp_id: str          # e.g. "q_001"
    type: str             # "single" | "multi" | "judge" | "fill" | "essay"
    content: str          # question stem text
    options: list[dict] = []   # [{"label": "A", "content": "..."}]
    answer: str = ""      # correct answer
    score: float = 0.0
    explanation: str = ""


class ParseResult(BaseModel):
    """Word 试卷解析结果"""

    filename: str
    questions: list[ParsedQuestion]
    total_count: int
    type_summary: dict[str, int]  # e.g. {"single": 10, "multi": 5, ...}
