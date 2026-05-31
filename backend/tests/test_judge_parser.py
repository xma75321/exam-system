"""判断题解析测试"""

import io
import pytest
import tempfile
import os
from docx import Document

from app.services.word_parser.extractor import extract_text
from app.services.word_parser.splitter import split_questions
from app.services.word_parser.judge_parser import parse_judge


def _create_and_parse(paragraphs: list[str]) -> dict:
    """创建 docx 并返回第一个解析块"""
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(buffer.read())
        tmp_path = tmp.name

    try:
        blocks = split_questions(extract_text(tmp_path))
        return blocks[0]
    finally:
        os.unlink(tmp_path)


class TestJudgeParser:
    """判断题解析测试"""

    def test_standard_correct(self):
        """标准正确答案"""
        block = _create_and_parse([
            "三、判断题（每题 1 分）",
            "1. Python 是面向对象的语言。（  ）",
            "答案：正确",
        ])
        result = parse_judge(block)
        assert result.type == "judge"
        assert "Python" in result.content
        assert result.answer == "正确"

    def test_standard_wrong(self):
        """标准错误答案"""
        block = _create_and_parse([
            "三、判断题",
            "1. Python 是编译型语言。（  ）",
            "答案：错误",
        ])
        result = parse_judge(block)
        assert result.answer == "错误"

    def test_answer_variant_dui(self):
        """答案：对"""
        block = _create_and_parse([
            "三、判断题",
            "1. 测试题",
            "答案：对",
        ])
        result = parse_judge(block)
        assert result.answer == "正确"

    def test_answer_variant_cuo(self):
        """答案：错"""
        block = _create_and_parse([
            "三、判断题",
            "1. 测试题",
            "答案：错",
        ])
        result = parse_judge(block)
        assert result.answer == "错误"

    def test_answer_variant_checkmark(self):
        """答案：√ / × 格式"""
        block = _create_and_parse([
            "三、判断题",
            "1. 测试题",
            "答案：√",
        ])
        result = parse_judge(block)
        assert result.answer == "正确"

        block2 = _create_and_parse([
            "三、判断题",
            "1. 测试题2",
            "答案：×",
        ])
        result2 = parse_judge(block2)
        assert result2.answer == "错误"

    def test_answer_variant_true_false(self):
        """答案：True / False"""
        block = _create_and_parse([
            "三、判断题",
            "1. 测试题",
            "答案：True",
        ])
        assert parse_judge(block).answer == "正确"

        block2 = _create_and_parse([
            "三、判断题",
            "1. 测试题2",
            "答案：False",
        ])
        assert parse_judge(block2).answer == "错误"

    def test_stem_number_removed(self):
        """题干题号被去除"""
        block = _create_and_parse([
            "三、判断题",
            "1. Python 是解释型语言。（  ）",
            "答案：正确",
        ])
        result = parse_judge(block)
        # 内容不应以"1."开头
        assert not result.content.startswith("1.")
        assert "Python" in result.content
        assert "（  ）" in result.content

    def test_ref_answer_prefix(self):
        """参考答案：前缀"""
        block = _create_and_parse([
            "三、判断题",
            "1. 测试题",
            "参考答案：正确",
        ])
        result = parse_judge(block)
        assert result.answer == "正确"
