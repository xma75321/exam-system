# TASK-020：答题 API

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：5 小时
- **依赖**：TASK-015
- **前置条件**：考试管理 API 已完成

## 任务描述
实现在线答题相关 API，包括开始考试、获取答题进度、保存答案和提交考试。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/routers/attempts.py` | 创建 | 答题路由 |
| 2 | `backend/app/services/attempt_service.py` | 创建 | 答题服务 |
| 3 | `backend/app/schemas/attempt.py` | 创建 | 答题请求/响应模型 |
| 4 | `backend/tests/test_attempts_api.py` | 创建 | 答题 API 测试 |

## 详细要求

### backend/app/routers/attempts.py
- `POST /api/attempts`：开始考试
  - 请求：exam_id
  - 验证考试状态为 open
  - 创建 exam_attempt 记录
  - 为每道题创建 question_response 记录（pending 状态）
  - 返回 attempt 信息和题目列表（不含答案）

- `GET /api/attempts/:id`：获取答题进度
  - 返回 attempt 信息和已保存的答案

- `PUT /api/attempts/:id/answers`：保存答案
  - 请求：answers 列表（question_id, user_answer）
  - 验证 attempt 状态为 in_progress
  - 验证答题时间未超时
  - 更新 question_response 记录

- `POST /api/attempts/:id/submit`：提交考试
  - 验证 attempt 状态为 in_progress
  - 更新 attempt 状态为 submitted
  - 记录提交时间
  - 触发自动评分（TASK-025）

### backend/app/services/attempt_service.py
- `start_exam(exam_id, user_id)`：开始考试
- `get_attempt(attempt_id)`：获取进度
- `save_answers(attempt_id, answers)`：保存答案
- `submit_exam(attempt_id)`：提交并触发评分

### backend/app/schemas/attempt.py
- `AttemptStart`：exam_id
- `AttemptResponse`：id, exam_id, status, started_at, end_time, questions
- `AnswerSave`：answers(list of question_id + user_answer)
- `AttemptSubmit`：无请求体

### backend/tests/test_attempts_api.py
- 开始考试成功
- 重复参加同一考试返回 400
- 考试未开放时不能参加
- 保存答案成功
- 提交考试成功
- 提交后不能再保存答案
- 超时后不能保存答案

## 验收标准
1. 开始考试创建 attempt 和所有 response 记录
2. 答题题目列表不含正确答案
3. 保存答案成功更新 response
4. 提交后状态变为 submitted
5. 已提交的考试不能重复保存
6. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_attempts_api.py -v
```
