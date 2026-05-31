"""填空题解析器 — 从题目块中提取填空题"""

import re
import logging

from app.services.word_parser.answer_parser import extract_answer, normalize_answer
from app.services.word_parser.models import ParsedQuestion

logger = logging.getLogger(__name__)


def parse_fill(block: dict) -> ParsedQuestion:
    """解析填空题。

    支持单空和多空题，答案分隔符包括逗号、分号、竖线。

    Args:
        block: split_questions 输出的题目块字典

    Returns:
        ParsedQuestion(type="fill")
    """
    stem = block.get("stem", "")

    # 去除题号前缀
    stripped = stem.strip()
    if stripped and stripped[0].isdigit():
        stem = re.sub(r"^\d+[\.\、\）\)]\s*", "", stripped)

    # 解析答案 — 填空答案用简单文本清理
    raw_answer = extract_answer(block.get("answer_line", ""))
    answer = raw_answer.strip() if raw_answer else ""

    section_info = block.get("section_info", {})
    score = section_info.get("score", 0.0)

    return ParsedQuestion(
        temp_id="",
        type="fill",
        content=stem,
        options=[],
        answer=answer,
        score=score,
        explanation="",
    )
