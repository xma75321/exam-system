# TASK-012：简答题解析

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：2 小时
- **依赖**：TASK-008
- **前置条件**：Word 解析引擎基础框架已完成

## 任务描述
实现简答题的解析逻辑，从 Word 段落块中提取题干和参考答案。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/services/word_parser/essay_parser.py` | 创建 | 简答题解析器 |
| 2 | `backend/tests/test_essay_parser.py` | 创建 | 简答题解析测试 |

## 详细要求

### backend/app/services/word_parser/essay_parser.py
- `parse_essay(block: dict)`：解析简答题
  - 提取题干（答案行之前的所有内容）
  - 提取参考答案（答案行及后续内容，直到下一题或文档结束）
  - 参考答案可能跨多行
  - 返回 ParsedQuestion(type="essay")

### 识别特征
- 无选项（没有 A/B/C/D 开头的行）
- 无填空占位符
- 答案格式：`答案：` 后跟长文本
- 参考答案可能包含多个段落

### 答案处理
- 保留答案的段落结构
- 去除答案前缀（`答案：`）
- 保留换行符（使用 `\n` 连接多行）

### backend/tests/test_essay_parser.py
- 简单简答题（单行答案）
- 复杂简答题（多行答案）
- 含多个段落的参考答案
- 无参考答案的简答题（答案行为空）

## 验收标准
1. 简答题可正确解析为 type=essay
2. 多行参考答案正确保留结构
3. 无参考答案时 answer 为空字符串
4. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_essay_parser.py -v
```
