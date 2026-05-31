"""判断题解析器 — 从题目块中提取判断题"""

import logging

from app.services.word_parser.answer_parser import extract_answer, normalize_answer
from app.services.word_parser.models import ParsedQuestion

logger = logging.getLogger(__name__)


def parse_judge(block: dict) -> ParsedQuestion:
    """解析判断题。

    Args:
        block: split_questions 输出的题目块字典

    Returns:
        ParsedQuestion(type="judge")
    """
    stem = block.get("stem", "")

    # 去除题号前缀
    stripped = stem.strip()
    # 处理数字开头：1. / 1、/ 1）
    if stripped and stripped[0].isdigit():
        import re
        stem = re.sub(r"^\d+[\.\、\）\)]\s*", "", stripped)

    # 解析答案
    raw_answer = extract_answer(block.get("answer_line", ""))
    answer = normalize_answer(raw_answer, "judge")

    section_info = block.get("section_info", {})
    score = section_info.get("score", 0.0)

    return ParsedQuestion(
        temp_id="",
        type="judge",
        content=stem,
        options=[],
        answer=answer,
        score=score,
        explanation="",
    )
