"""简答题解析测试"""

import io
import pytest
import tempfile
import os
from docx import Document

from app.services.word_parser.extractor import extract_text
from app.services.word_parser.splitter import split_questions
from app.services.word_parser.essay_parser import parse_essay


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


class TestEssayParser:
    """简答题解析测试"""

    def test_simple_essay(self):
        """简单简答题"""
        block = _create_and_parse([
            "五、简答题（每题 5 分）",
            "1. 简述 Python 的特点。",
            "答案：Python 具有简洁易读的语法、丰富的标准库、跨平台等特点。",
        ])
        result = parse_essay(block)
        assert result.type == "essay"
        assert "Python 的特点" in result.content
        assert "简洁易读" in result.answer

    def test_multi_line_answer(self):
        """多行参考答案"""
        block = _create_and_parse([
            "五、简答题",
            "1. 解释面向对象编程的三大特性。",
            "答案：封装：将数据和操作封装在类中，隐藏内部实现。",
            "继承：子类可以继承父类的属性和方法。",
            "多态：同一操作作用于不同对象，可以有不同的解释。",
        ])
        result = parse_essay(block)
        assert result.type == "essay"
        assert len(result.answer) > 0

    def test_no_answer(self):
        """无参考答案"""
        block = _create_and_parse([
            "五、简答题",
            "1. 谈谈你对人工智能的理解。",
        ])
        result = parse_essay(block)
        assert result.type == "essay"
        assert result.answer == ""

    def test_stem_number_removed(self):
        """题号被去除"""
        block = _create_and_parse([
            "五、简答题",
            "1. 简述 Python 的特点。",
            "答案：Python 语言简洁。",
        ])
        result = parse_essay(block)
        assert not result.content.startswith("1.")
        assert "Python" in result.content

    def test_ref_answer_prefix(self):
        """参考答案：前缀"""
        block = _create_and_parse([
            "五、简答题",
            "1. 简述数据类型。",
            "参考答案：Python 支持 int、float、str 等数据类型。",
        ])
        result = parse_essay(block)
        assert "int" in result.answer
