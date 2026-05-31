"""选择题解析测试"""

import io
import pytest
from docx import Document

from app.services.word_parser.choice_parser import parse_choice
from app.services.word_parser.splitter import split_questions
from app.services.word_parser.extractor import extract_text


def _create_docx(paragraphs: list[str]) -> io.BytesIO:
    """创建包含指定段落的 .docx 文件"""
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def _parse_blocks(docx_buffer: io.BytesIO) -> list[dict]:
    """从 .docx 中解析题目块"""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(docx_buffer.read())
        tmp_path = tmp.name

    try:
        paragraphs = extract_text(tmp_path)
        return split_questions(paragraphs)
    finally:
        os.unlink(tmp_path)


def _get_first_block(blocks: list[dict]) -> dict:
    """获取第一个题目块"""
    assert len(blocks) > 0, "没有解析到题目块"
    return blocks[0]


class TestSingleChoice:
    """单选题解析测试"""

    def test_standard_format(self):
        """标准格式单选题"""
        docx = _create_docx([
            "一、单选题（每题 2 分，共 20 分）",
            "1. Python 是什么类型的语言？",
            "A. 编译型",
            "B. 解释型",
            "C. 汇编型",
            "D. 机器语言",
            "答案：B",
        ])
        blocks = _parse_blocks(docx)
        result = parse_choice(_get_first_block(blocks), "single")

        assert result.type == "single"
        assert "Python" in result.content
        assert result.answer == "B"
        assert len(result.options) == 4
        assert result.options[0] == {"label": "A", "content": "编译型"}
        assert result.options[1]["label"] == "B"
        assert result.options[2]["label"] == "C"
        assert result.options[3]["label"] == "D"

    def test_option_format_variants(self):
        """不同选项分隔符变体"""
        docx = _create_docx([
            "一、单选题（每题 2 分）",
            "1. 测试题",
            "A、选项一",
            "B、选项二",
            "C）选项三",
            "答案：A",
        ])
        blocks = _parse_blocks(docx)
        result = parse_choice(_get_first_block(blocks), "single")

        assert result.type == "single"
        assert result.answer == "A"
        assert len(result.options) == 3
        assert result.options[0]["content"] == "选项一"

    def test_lowercase_option_labels(self):
        """小写选项标签自动转大写"""
        docx = _create_docx([
            "一、单选题",
            "1. 测试题",
            "a. 选项A",
            "b. 选项B",
            "答案：a",
        ])
        blocks = _parse_blocks(docx)
        result = parse_choice(_get_first_block(blocks), "single")

        assert result.options[0]["label"] == "A"
        assert result.options[1]["label"] == "B"
        assert result.answer == "A"


class TestMultiChoice:
    """多选题解析测试"""

    def test_standard_multi(self):
        """标准格式多选题"""
        docx = _create_docx([
            "二、多选题（每题 3 分）",
            "1. 以下哪些是 Python 的数据类型？",
            "A. int",
            "B. float",
            "C. char",
            "D. str",
            "答案：A,B,D",
        ])
        blocks = _parse_blocks(docx)
        result = parse_choice(_get_first_block(blocks), "multi")

        assert result.type == "multi"
        assert result.answer == "A,B,D"
        assert len(result.options) == 4

    def test_multi_option_crossline(self):
        """选项内容跨行合并"""
        docx = _create_docx([
            "二、多选题",
            "1. 跨行选项测试",
            "A. 这是第一行的内容",
            "  续接第二行",
            "B. 正常选项",
            "答案：A",
        ])
        blocks = _parse_blocks(docx)
        result = parse_choice(_get_first_block(blocks), "single")

        assert len(result.options) == 2
        assert "续接第二行" in result.options[0]["content"]


class TestEdgeCases:
    """边界情况测试"""

    def test_missing_answer(self):
        """缺少答案的题目处理"""
        docx = _create_docx([
            "一、单选题",
            "1. 无答案题目",
            "A. 选项一",
            "B. 选项二",
        ])
        blocks = _parse_blocks(docx)
        result = parse_choice(_get_first_block(blocks), "single")

        # 不抛异常，答案为空的正常结果
        assert result.type == "single"
        assert result.answer == ""
        assert len(result.options) == 2

    def test_answer_colon_variant(self):
        """答案冒号变体"""
        test_cases = [
            "答案：B",
            "答案:B",
            "参考答案：B",
            "参考答案:B",
            "答：B",
            "答:B",
        ]
        for answer_text in test_cases:
            docx = _create_docx([
                "一、单选题",
                "1. 测试题",
                "A. 选项一",
                "B. 选项二",
                answer_text,
            ])
            blocks = _parse_blocks(docx)
            result = parse_choice(_get_first_block(blocks), "single")
            assert result.answer == "B", f"Failed for: {answer_text}"
