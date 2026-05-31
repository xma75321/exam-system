"""简答题解析器 — 从题目块中提取简答题"""

import re
import logging

from app.services.word_parser.answer_parser import extract_answer
from app.services.word_parser.models import ParsedQuestion

logger = logging.getLogger(__name__)


def parse_essay(block: dict) -> ParsedQuestion:
    """解析简答题。

    答案可能跨多行，保留换行符连接。

    Args:
        block: split_questions 输出的题目块字典

    Returns:
        ParsedQuestion(type="essay")
    """
    stem = block.get("stem", "")

    # 去除题号前缀
    stripped = stem.strip()
    if stripped and stripped[0].isdigit():
        stem = re.sub(r"^\d+[\.\、\）\)]\s*", "", stripped)

    # 解析参考答案
    answer_line = block.get("answer_line", "")
    raw_answer = extract_answer(answer_line)
    answer = raw_answer.strip() if raw_answer else ""

    section_info = block.get("section_info", {})
    score = section_info.get("score", 0.0)

    return ParsedQuestion(
        temp_id="",
        type="essay",
        content=stem,
        options=[],
        answer=answer,
        score=score,
        explanation="",
    )
