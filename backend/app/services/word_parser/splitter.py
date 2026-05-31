"""题目分割器 — 将文档段落分割为独立的题目块"""

import logging

logger = logging.getLogger(__name__)

# 题型关键词映射
SECTION_TYPE_MAP = {
    "单选题": "single",
    "单选": "single",
    "多选题": "multi",
    "多选": "multi",
    "判断题": "judge",
    "判断": "judge",
    "填空题": "fill",
    "填空": "fill",
    "简答题": "essay",
    "简答": "essay",
}

# 选项标记字符
OPTION_LABELS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
OPTION_SEPARATORS = ".、）)"


def _detect_section_type(line: str) -> tuple[str | None, float, str]:
    """检测是否为章节标题，返回 (section_type, default_score, section_title)。"""
    stripped = line.strip()
    section_type: str | None = None

    for keyword, mapped_type in SECTION_TYPE_MAP.items():
        if keyword in stripped:
            section_type = mapped_type
            break

    if section_type is None:
        return None, 0.0, stripped

    # 尝试提取分数，如 "每题 2 分" 或 "每题2分"
    default_score = 0.0
    if "每题" in stripped:
        after = stripped.split("每题")[1]
        # 取后续字符中的第一个数字
        num_str = ""
        for ch in after:
            if ch.isdigit() or ch == ".":
                num_str += ch
            elif num_str:
                break
        if num_str:
            try:
                default_score = float(num_str)
            except ValueError:
                default_score = 0.0

    return section_type, default_score, stripped


def _is_question_start(line: str) -> tuple[bool, int]:
    """检测行是否为题号开头，返回 (is_start, number)。"""
    stripped = line.strip()
    if not stripped:
        return False, 0

    # 处理全角括号形式：（1）
    if stripped.startswith("（") or stripped.startswith("("):
        inner = stripped[1:]
        num_str = ""
        for ch in inner:
            if ch.isdigit():
                num_str += ch
            else:
                break
        if num_str and (inner[len(num_str):].startswith("）") or inner[len(num_str):].startswith(")")):
            return True, int(num_str)
        return False, 0

    # 处理普通数字开头：1.  1、  1)  1）
    num_str = ""
    for ch in stripped:
        if ch.isdigit():
            num_str += ch
        else:
            break
    if not num_str:
        return False, 0

    rest = stripped[len(num_str):]
    if rest and rest[0] in ".、）)":
        return True, int(num_str)

    return False, 0


def _is_option_line(line: str) -> tuple[bool, str, str]:
    """检测行是否为选项，返回 (is_option, label, content)。"""
    stripped = line.strip()
    if len(stripped) < 2:
        return False, "", ""

    first_char = stripped[0]
    if first_char not in OPTION_LABELS:
        return False, "", ""

    second_char = stripped[1]
    if second_char in OPTION_SEPARATORS or second_char.isspace():
        label = first_char.upper()
        content = stripped[2:].strip()
        # 如果分隔符后紧跟空格，再 strip 一次
        if content.startswith(".") or content.startswith("。"):
            content = content[1:].strip()
        return True, label, content

    return False, "", ""


def _is_answer_line(line: str) -> tuple[bool, str]:
    """检测行是否为答案行，返回 (is_answer, answer_text)。"""
    stripped = line.strip()
    if not stripped:
        return False, ""

    # 匹配 "答案：" / "参考答案：" / "答：" 及其半角变体
    prefixes = ["参考答案：", "参考答案:", "答案：", "答案:", "答：", "答:"]
    for prefix in prefixes:
        if stripped.startswith(prefix):
            return True, stripped[len(prefix):].strip()

    # 也支持答案不在开头的情况，如 "答案：B" 出现在行中间（较少见）
    for marker in ["答案：", "答案:", "参考答案：", "参考答案:", "答：", "答:"]:
        idx = stripped.find(marker)
        if idx != -1:
            return True, stripped[idx + len(marker):].strip()

    return False, ""


def split_questions(paragraphs: list[str]) -> list[dict]:
    """将段落列表分割为独立的题目块。

    Args:
        paragraphs: 从 Word 文档提取的非空文本行列表

    Returns:
        题目块字典列表，每个字典包含 number, stem, options, answer_line, section_info
    """
    blocks: list[dict] = []
    current_block_lines: list[str] = []
    current_number: int = 0
    current_section_type: str = ""
    current_section_score: float = 0.0

    def _flush_block() -> None:
        """将当前缓存的行保存为一个题目块。"""
        nonlocal current_block_lines, current_number
        if not current_block_lines or current_number == 0:
            current_block_lines = []
            current_number = 0
            return

        stem_lines: list[str] = []
        option_lines: list[str] = []
        answer_line: str = ""
        in_options: bool = False

        for line in current_block_lines:
            is_opt, _, _ = _is_option_line(line)
            is_ans, ans_text = _is_answer_line(line)

            if is_opt:
                option_lines.append(line)
                in_options = True
            elif is_ans:
                answer_line = ans_text
                in_options = False
            elif in_options and line.strip():
                # 选项内容跨行续接
                option_lines.append(line)
            elif not is_ans:
                stem_lines.append(line)
                in_options = False

        # 题干：去掉第一行的题号前缀
        stem = "\n".join(stem_lines).strip()
        blocks.append({
            "number": current_number,
            "stem": stem,
            "options": option_lines,
            "answer_line": answer_line,
            "section_info": {
                "type": current_section_type,
                "score": current_section_score,
            },
        })
        current_block_lines = []
        current_number = 0

    for line in paragraphs:
        # 先检测是否是章节标题
        sec_type, sec_score, _ = _detect_section_type(line)
        if sec_type is not None:
            _flush_block()
            current_section_type = sec_type
            current_section_score = sec_score
            continue

        # 检测是否是新题号
        is_q_start, q_num = _is_question_start(line)
        if is_q_start:
            _flush_block()
            current_number = q_num
            current_block_lines.append(line)
            continue

        # 普通内容行，归入当前块
        if current_number > 0:
            current_block_lines.append(line)
        else:
            # 未进入任何题目前的内容，直接忽略
            logger.warning("跳过未归属内容: %s", line)

    # 处理最后一个块
    _flush_block()

    return blocks
