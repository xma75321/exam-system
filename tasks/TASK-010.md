# TASK-010：判断题解析

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：2 小时
- **依赖**：TASK-008
- **前置条件**：Word 解析引擎基础框架已完成

## 任务描述
实现判断题的解析逻辑，从 Word 段落块中提取题干和正确/错误答案。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/services/word_parser/judge_parser.py` | 创建 | 判断题解析器 |
| 2 | `backend/tests/test_judge_parser.py` | 创建 | 判断题解析测试 |

## 详细要求

### backend/app/services/word_parser/judge_parser.py
- `parse_judge(block: dict)`：解析判断题
  - 提取题干
  - 识别答案变体：
    - `正确` / `对` / `√` / `T` / `True` → 标准化为 `正确`
    - `错误` / `错` / `×` / `F` / `False` → 标准化为 `错误`
  - 题干中可能含 `（  ）` 或 `___` 作为填空标记
  - 返回 ParsedQuestion(type="judge")

### 识别规则
- 答案行为 `答案：正确` 或 `答案：错误` 等
- 如果题干包含 `（  ）` 且答案为对错类，则为判断题
- 与填空题区分：判断题的答案是有限枚举值

### backend/tests/test_judge_parser.py
- 标准格式：`答案：正确` / `答案：错误`
- 变体格式：`答案：对` / `答案：错` / `答案：√` / `答案：×`
- 英文格式：`答案：T` / `答案：True`
- 带括号的题干：`Python 是解释型语言。（  ）`

## 验收标准
1. 标准判断题可正确解析为 type=judge
2. 答案统一标准化为 `正确` 或 `错误`
3. 支持所有定义的变体格式
4. 带括号的题干能正确识别
5. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_judge_parser.py -v
```
