# TASK-009：选择题解析

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：4 小时
- **依赖**：TASK-008
- **前置条件**：Word 解析引擎基础框架已完成

## 任务描述
实现单选题和多选题的解析逻辑，从 Word 段落块中提取题干、选项、正确答案。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/services/word_parser/choice_parser.py` | 创建 | 选择题解析器 |
| 2 | `backend/app/services/word_parser/answer_parser.py` | 创建 | 答案行解析工具 |
| 3 | `backend/tests/test_choice_parser.py` | 创建 | 选择题解析测试 |
| 4 | `backend/tests/test_data/sample_choice.docx` | 创建 | 测试用 Word 文件（代码生成） |

## 详细要求

### backend/app/services/word_parser/choice_parser.py
- `parse_single_choice(block: dict)`：解析单选题
  - 提取题干（题号之后、选项之前的内容）
  - 提取选项（A/B/C/D 开头的行）
  - 提取答案（单个字母）
  - 返回 ParsedQuestion(type="single")

- `parse_multi_choice(block: dict)`：解析多选题
  - 选项提取同单选
  - 答案为多个逗号分隔字母（如 `A,B,D`）
  - 返回 ParsedQuestion(type="multi")

- 选项解析容错：
  - `A.` / `A、` / `A）` / `(A)` 均可识别
  - 小写字母自动转大写
  - 选项内容可跨多行

### backend/app/services/word_parser/answer_parser.py
- `extract_answer(block: dict)`：从题目块中提取答案行
- 支持答案格式变体：`答案：` / `参考答案：` / `答：` / `Answer:`
- 返回原始答案字符串

### backend/tests/test_choice_parser.py
- 标准格式单选题解析
- 格式变体单选题解析（不同选项标记）
- 多选题解析
- 缺少答案的题目处理
- 选项跨行处理

## 验收标准
1. 标准格式单选题可正确解析为 type=single，选项完整，答案正确
2. 多选题可正确解析为 type=multi，答案为逗号分隔字符串
3. 支持多种选项标记格式（A. / A、 / (A)）
4. 小写选项标签自动转大写
5. 缺少答案的题目标记为解析异常但不中断整体流程
6. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_choice_parser.py -v
```
