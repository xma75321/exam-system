"""Word 试卷解析主入口 — 编排提取、分割、分类全流程"""

import logging
import os

from fastapi import HTTPException

from app.services.word_parser.classifier import classify_question
from app.services.word_parser.extractor import extract_text
from app.services.word_parser.models import ParseResult, ParsedQuestion
from app.services.word_parser.splitter import split_questions

logger = logging.getLogger(__name__)


def parse_word_document(file_path: str) -> ParseResult:
    """解析 Word 试卷文件，返回结构化题目数据。

    Args:
        file_path: .docx 文件的磁盘路径

    Returns:
        ParseResult 包含所有解析出的题目及统计信息

    Raises:
        HTTPException: 解析失败时抛出，错误码 2003
    """
    try:
        filename = os.path.basename(file_path)

        # 1. 提取文本
        paragraphs = extract_text(file_path)
        if not paragraphs:
            logger.warning("文档为空或无法读取文本: %s", file_path)
            return ParseResult(
                filename=filename,
                questions=[],
                total_count=0,
                type_summary={},
            )

        # 2. 分割为题目块
        blocks = split_questions(paragraphs)

        # 3. 分类并构建模型
        questions: list[ParsedQuestion] = []
        type_summary: dict[str, int] = {}

        for idx, block in enumerate(blocks, start=1):
            try:
                q_type, options, answer = classify_question(block)
                section_info = block.get("section_info", {})
                score = section_info.get("score", 0.0)

                question = ParsedQuestion(
                    temp_id=f"q_{idx:03d}",
                    type=q_type,
                    content=block.get("stem", ""),
                    options=options,
                    answer=answer,
                    score=score,
                    explanation="",
                )
                questions.append(question)
                type_summary[q_type] = type_summary.get(q_type, 0) + 1
            except Exception as e:
                logger.warning("题目块解析失败，已跳过: %s", e)
                continue

        return ParseResult(
            filename=filename,
            questions=questions,
            total_count=len(questions),
            type_summary=type_summary,
        )

    except Exception as e:
        logger.exception("Word 文件解析失败: %s", file_path)
        raise HTTPException(
            status_code=500,
            detail={
                "code": 2003,
                "message": f"文件解析失败: {str(e)}",
            },
        ) from e
