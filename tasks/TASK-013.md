# TASK-013：题库确认入库 API

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：4 小时
- **依赖**：TASK-009, TASK-010, TASK-011, TASK-012
- **前置条件**：所有题型解析器已完成

## 任务描述
实现解析结果确认入库接口，将用户确认后的解析结果保存到数据库（questions + options 表）。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/routers/upload.py` | 修改 | 添加确认入库端点 |
| 2 | `backend/app/services/question_service.py` | 创建 | 题目入库服务 |
| 3 | `backend/app/schemas/question.py` | 创建 | 题目相关请求/响应模型 |
| 4 | `backend/tests/test_question_save.py` | 创建 | 入库测试 |

## 详细要求

### backend/app/routers/upload.py（修改）
- `POST /api/upload/confirm`：确认解析结果并入库
- 请求体包含文件名和题目列表（解析结果 JSON）
- 调用 question_service 批量创建题目
- 返回保存后的题目列表（含真实 ID）

### backend/app/services/question_service.py
- `save_questions(questions: list, user_id: int)`：
  - 创建 exam 记录（标题为文件名，状态为 draft）
  - 逐题创建 question 记录
  - 选择题创建 options 记录
  - 使用事务保证原子性
  - 返回创建的题目列表

### backend/app/schemas/question.py
- `QuestionSaveRequest`：filename, questions(list)
- `QuestionSaveItem`：temp_id, type, content, options, answer, score, explanation
- `QuestionSaveResponse`：exam_id, questions(list with real IDs)

### backend/tests/test_question_save.py
- 保存混合题型试卷
- 选项正确关联到题目
- 事务回滚（部分题目异常时整体回滚）
- 返回的 ID 可用于后续查询

## 验收标准
1. `POST /api/upload/confirm` 可将解析结果存入数据库
2. questions 表正确存储所有题型
3. 选择题的 options 正确关联
4. 创建了对应的 exam 记录
5. 异常时数据回滚，不产生脏数据
6. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_question_save.py -v

# 手动测试
curl -X POST http://localhost:8000/api/upload/confirm \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"filename":"test.docx","questions":[{"temp_id":"q1","type":"single","content":"测试题","options":[{"label":"A","content":"选项A"},{"label":"B","content":"选项B"}],"answer":"A","score":2}]}'
```
