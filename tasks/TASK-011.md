# TASK-011：填空题解析

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：2 小时
- **依赖**：TASK-008
- **前置条件**：Word 解析引擎基础框架已完成

## 任务描述
实现填空题的解析逻辑，从 Word 段落块中提取题干和填空答案。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/services/word_parser/fill_parser.py` | 创建 | 填空题解析器 |
| 2 | `backend/tests/test_fill_parser.py` | 创建 | 填空题解析测试 |

## 详细要求

### backend/app/services/word_parser/fill_parser.py
- `parse_fill(block: dict)`：解析填空题
  - 提取题干（含下划线/空格占位符的部分）
  - 提取填空答案
  - 支持多空题：答案用逗号或分号分隔
  - 返回 ParsedQuestion(type="fill")

### 识别特征
- 题干包含 `______`（连续下划线）或 `___` 或 `(    )`
- 答案格式：`答案：xxx` 或 `答案：xxx, yyy`（多空）
- 答案标准化：去除首尾空格

### 多空处理
- 如果题干有 N 个填空位，答案应有 N 个值
- 答案分隔符支持：逗号（中英文）、分号、竖线
- 存储格式：逗号分隔字符串

### backend/tests/test_fill_parser.py
- 单空填空题
- 多空填空题
- 不同占位符格式（下划线、括号空格）
- 答案含多种分隔符
- 答案多余空格自动去除

## 验收标准
1. 单空填空题可正确解析为 type=fill
2. 多空题答案正确分割和存储
3. 题干中的占位符保留原始格式
4. 答案首尾空格自动去除
5. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_fill_parser.py -v
```
