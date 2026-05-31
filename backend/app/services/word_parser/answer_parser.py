"""答案行解析工具 — 从题目块中提取和规范化答案"""

import logging

logger = logging.getLogger(__name__)

# 答案行前缀匹配
ANSWER_PREFIXES = [
    "参考答案：",
    "参考答案:",
    "答案：",
    "答案:",
    "答：",
    "答:",
    "Answer:",
    "answer:",
]


def extract_answer(answer_line: str) -> str:
    """从答案行文本中提取原始答案字符串。

    支持多种格式变体：
    - "答案：B" → "B"
    - "参考答案：A,B,D" → "A,B,D"
    - "答：正确" → "正确"
    - "Answer: B" → "B"

    Args:
        answer_line: 包含答案的原始文本行

    Returns:
        去除前缀后的答案文本（trimmed）
    """
    stripped = answer_line.strip()
    if not stripped:
        return ""

    for prefix in ANSWER_PREFIXES:
        if stripped.startswith(prefix):
            return stripped[len(prefix):].strip()

    # 如果行中没有已知前缀，但文本非空，视为直接答案
    return stripped


def normalize_answer(raw_answer: str, question_type: str) -> str:
    """根据题型规范化答案。

    - 选择题（single/multi）：去除多余空格，大写字母
    - 判断题（judge）：统一为 "正确" / "错误"
    - 填空题（fill）、简答题（essay）：保留原文

    Args:
        raw_answer: extract_answer 输出的原始答案
        question_type: single | multi | judge | fill | essay

    Returns:
        规范化后的答案字符串
    """
    if not raw_answer:
        return ""

    if question_type in ("single", "multi"):
        # 去除空格，转为大写
        normalized = raw_answer.replace(" ", "").upper()
        return normalized

    if question_type == "judge":
        # 判断题变体统一
        judge_map = {
            "正确": "正确",
            "对": "正确",
            "√": "正确",
            "是": "正确",
             "yes": "正确",
            "true": "正确",
            "错误": "错误",
            "错": "错误",
            "×": "错误",
            "否": "错误",
            "no": "错误",
            "false": "错误",
            "不对": "错误",
        }
        return judge_map.get(raw_answer.lower(), raw_answer)

    return raw_answer
