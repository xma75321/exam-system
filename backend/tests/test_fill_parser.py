"""填空题解析测试"""

import io
import pytest
import tempfile
import os
from docx import Document

from app.services.word_parser.extractor import extract_text
from app.services.word_parser.splitter import split_questions
from app.services.word_parser.fill_parser import parse_fill


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


class TestFillParser:
    """填空题解析测试"""

    def test_single_fill_underscore(self):
        """单空 + 下划线占位"""
        block = _create_and_parse([
            "四、填空题（每题 2 分）",
            "1. Python 中定义函数使用的关键字是 ______。",
            "答案：def",
        ])
        result = parse_fill(block)
        assert result.type == "fill"
        assert "______" in result.content
        assert result.answer == "def"

    def test_single_fill_triple_underscore(self):
        """单空 + ___ 占位"""
        block = _create_and_parse([
            "四、填空题",
            "1. 变量的命名规则使用 ___ 连接。",
            "答案：下划线",
        ])
        result = parse_fill(block)
        assert result.type == "fill"
        assert result.answer == "下划线"

    def test_multi_fill(self):
        """多空题"""
        block = _create_and_parse([
            "四、填空题",
            "1. Python 的数据类型有 ______、______ 和 ______。",
            "答案：int, float, str",
        ])
        result = parse_fill(block)
        assert result.type == "fill"
        assert result.answer == "int, float, str"

    def test_answer_with_spaces(self):
        """答案含多余空格自动去除"""
        block = _create_and_parse([
            "四、填空题",
            "1. 测试题",
            "答案：   def   ",
        ])
        result = parse_fill(block)
        # 两端空格被去除，中间空格保留
        assert result.answer == "def"

    def test_answer_semicolon_separator(self):
        """答案用分号分隔"""
        block = _create_and_parse([
            "四、填空题",
            "1. 多空测试题",
            "答案：Python; Java; C++",
        ])
        result = parse_fill(block)
        assert "Python" in result.answer
        assert "Java" in result.answer

    def test_stem_number_removed(self):
        """题号被去除但保留占位符"""
        block = _create_and_parse([
            "四、填空题",
            "1. 测试关键字 ______。",
            "答案：test",
        ])
        result = parse_fill(block)
        assert not result.content.startswith("1.")
        assert "______" in result.content
