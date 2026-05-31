"""题目分类器 — 根据文本特征判断题型并规范化选项和答案"""

import logging

from app.services.word_parser.splitter import _is_option_line

logger = logging.getLogger(__name__)

# 判断题答案规范化映射
JUDGE_TRUE_VARIANTS = {"正确", "对", "√", "是", "yes", "true"}
JUDGE_FALSE_VARIANTS = {"错误", "错", "×", "否", "no", "false", "不对"}


def _normalize_judge_answer(answer: str) -> str:
    """将判断题答案的各种写法统一为 '正确' 或 '错误'。"""
    stripped = answer.strip()
    lower = stripped.lower()
    if lower in JUDGE_TRUE_VARIANTS:
        return "正确"
    if lower in JUDGE_FALSE_VARIANTS:
        return "错误"
    return stripped


def _parse_options(option_lines: list[str]) -> list[dict]:
    """将选项文本行解析为结构化列表。"""
    options: list[dict] = []
    seen_labels: set[str] = set()

    for line in option_lines:
        is_opt, label, content = _is_option_line(line)
        if not is_opt:
            continue
        if label in seen_labels:
            continue
        seen_labels.add(label)
        options.append({"label": label, "content": content})

    return options


def _clean_answer(answer_line: str, section_type: str) -> str:
    """清理答案文本，去除前缀并规范化。"""
    cleaned = answer_line.strip()

    # 去除常见前缀
    prefixes = ["参考答案：", "参考答案:", "答案：", "答案:", "答：", "答:"]
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break

    if section_type == "judge":
        cleaned = _normalize_judge_answer(cleaned)

    return cleaned


def classify_question(block: dict) -> tuple[str, list[dict], str]:
    """根据题目块内容判断题型，并解析选项和答案。

    Args:
        block: split_questions 生成的题目块字典

    Returns:
        (question_type, parsed_options, cleaned_answer)
    """
    stem = block.get("stem", "")
    option_lines = block.get("options", [])
    answer_line = block.get("answer_line", "")
    section_info = block.get("section_info", {})
    section_type = section_info.get("type", "")

    options = _parse_options(option_lines)
    cleaned_answer = _clean_answer(answer_line, section_type)

    # 分类规则（按优先级）
    question_type = "essay"  # 默认简答题

    # 规则 1 & 2：有选项 → 单选或多选
    if options:
        # 判断答案中是否包含逗号或多个字母
        if "," in cleaned_answer or "，" in cleaned_answer or len(cleaned_answer) > 1:
            question_type = "multi"
        else:
            question_type = "single"
    else:
        # 规则 3：判断题 — 内容含（  ）或答案为正确/错误
        if "（  ）" in stem or "(  )" in stem or "（　　）" in stem:
            question_type = "judge"
        elif cleaned_answer in ("正确", "错误"):
            question_type = "judge"
        # 规则 4：填空题 — 内容含下划线或连续空格
        elif "___" in stem or "______" in stem or "____" in stem:
            question_type = "fill"
        # 规则 5：否则为简答题
        else:
            question_type = "essay"

    # 如果 section_type 已经明确，且当前推断为 essay，优先使用 section_type
    # （用于处理无选项但 section 已标明为 judge/fill 的情况）
    if section_type and question_type == "essay" and section_type in ("judge", "fill"):
        question_type = section_type

    return question_type, options, cleaned_answer
