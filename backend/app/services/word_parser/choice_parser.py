"""选择题（单选/多选）解析器 — 从题目块中提取单选题和多选题"""

import logging

from app.services.word_parser.answer_parser import extract_answer, normalize_answer
from app.services.word_parser.models import ParsedQuestion
from app.services.word_parser.splitter import _is_option_line

logger = logging.getLogger(__name__)

# 选项标签分隔符
OPTION_SEPARATORS = ".、）)"


def _parse_choice_options(option_lines: list[str]) -> list[dict]:
    """将选项文本行解析为结构化选项列表。

    支持格式：
    - "A. 编译型" / "A、编译型" / "A）编译型" / "(A) 编译型"
    - 小写标签自动转大写
    - 选项内容跨行自动合并

    Args:
        option_lines: 选项文本行列表

    Returns:
        [{"label": "A", "content": "编译型"}, ...]
    """
    options: list[dict] = []
    current_option: dict | None = None

    for line in option_lines:
        is_opt, label, content = _is_option_line(line)

        if is_opt:
            # 新选项开始，保存上一个
            if current_option:
                options.append(current_option)
            current_option = {"label": label.upper(), "content": content}
        elif current_option:
            # 跨行续接：追加到当前选项内容
            stripped = line.strip()
            if stripped:
                current_option["content"] += " " + stripped

    # 保存最后一个选项
    if current_option:
        options.append(current_option)

    return options


def parse_choice(
    block: dict,
    question_type: str,
) -> ParsedQuestion:
    """解析选择题（单选或多项）。

    Args:
        block: split_questions 输出的题目块字典
        question_type: "single" 或 "multi"

    Returns:
        ParsedQuestion 对象
    """
    stem = block.get("stem", "")

    # 去除题干中的题号前缀
    stem = _clean_stem_number(stem)

    # 解析选项
    option_lines = block.get("options", [])
    options = _parse_choice_options(option_lines)

    # 解析答案
    raw_answer = extract_answer(block.get("answer_line", ""))
    answer = normalize_answer(raw_answer, question_type)

    # 分值
    section_info = block.get("section_info", {})
    score = section_info.get("score", 0.0)

    return ParsedQuestion(
        temp_id="",  # 由调用方设置
        type=question_type,
        content=stem,
        options=options,
        answer=answer,
        score=score,
        explanation="",
    )


def _clean_stem_number(stem: str) -> str:
    """去除题干开头的题号（如 '1. '、'1、'、'1）'）。"""
    stripped = stem.strip()
    if not stripped:
        return stripped

    # 处理全角括号：（1）题干
    if stripped.startswith("（") or stripped.startswith("("):
        end = stripped.find("）") if "（" in stripped[:3] else stripped.find(")")
        if end != -1 and end <= 3:
            stripped = stripped[end + 1:].strip()
            return stripped

    # 处理数字开头：1. 题干 / 1、题干 / 1）题干
    num_end = 0
    for i, ch in enumerate(stripped):
        if ch.isdigit():
            num_end = i + 1
        else:
            break

    if num_end > 0 and num_end < len(stripped) and stripped[num_end] in OPTION_SEPARATORS:
        stripped = stripped[num_end + 1:].strip()

    return stripped
