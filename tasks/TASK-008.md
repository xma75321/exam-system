# TASK-008：Word 解析引擎基础

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：6 小时
- **依赖**：TASK-007
- **前置条件**：文件上传 API 已完成

## 任务描述
实现 Word 文档解析引擎的核心框架，包括文档读取、段落分割、题型识别和基础解析流程。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/services/word_parser/__init__.py` | 创建 | 包初始化和对外接口 |
| 2 | `backend/app/services/word_parser/extractor.py` | 创建 | 文档内容提取 |
| 3 | `backend/app/services/word_parser/classifier.py` | 创建 | 题型分类器 |
| 4 | `backend/app/services/word_parser/splitter.py` | 创建 | 题目分割器 |
| 5 | `backend/app/services/word_parser/models.py` | 创建 | 解析中间数据模型 |

## 详细要求

### backend/app/services/word_parser/models.py
- `ParsedQuestion`：temp_id, type, content, options(list), answer, score, explanation
- `ParseResult`：filename, questions(list ParsedQuestion), total_count, type_summary(dict)
- 与 API 响应格式一致

### backend/app/services/word_parser/extractor.py
- `extract_text(file_path: str)`：使用 python-docx 读取文档
- 提取所有段落文本（保留段落结构）
- 提取表格内容（如果试卷中有表格形式的选项）
- 返回段落列表

### backend/app/services/word_parser/splitter.py
- `split_questions(paragraphs: list)`：将段落列表分割为独立题目
- 识别题号模式（`1.`、`1、`、`（1）` 等）
- 每道题包含：题号、题干、选项（如有）、答案行
- 返回题目段落块列表

### backend/app/services/word_parser/classifier.py
- `classify_question(block: dict)`：判断题目类型
- 规则：
  - 有 A/B/C/D 选项 + 单个答案 → single
  - 有 A/B/C/D 选项 + 多个逗号分隔答案 → multi
  - 题干含 `（  ）` 或答案为 正确/错误 → judge
  - 题干含下划线/空格占位 → fill
  - 其他 → essay

### backend/app/services/word_parser/__init__.py
- `parse_word_document(file_path: str)`：主入口函数
- 调用 extractor → splitter → 各题型解析器
- 返回 ParseResult

## 验收标准
1. 可读取 .docx 文件并提取所有段落文本
2. 可将文档正确分割为独立题目块
3. 可正确识别各题型
4. 解析流程串联正确：读取 → 分割 → 分类 → 返回结果
5. 对空文档、格式异常文档有容错处理

## 测试方法
```bash
cd backend
python -c "
from app.services.word_parser import parse_word_document
result = parse_word_document('test_data/sample.docx')
print(f'共解析 {result.total_count} 题')
for q in result.questions[:3]:
    print(f'[{q.type}] {q.content[:50]}...')
"
```
