# TASK-015：考试管理 API

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：6 小时
- **依赖**：TASK-014
- **前置条件**：题库 API 已完成

## 任务描述
实现考试管理接口，包括创建考试（从题库选题）、考试列表、详情、更新、删除和状态管理。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/routers/exams.py` | 创建 | 考试路由 |
| 2 | `backend/app/services/exam_service.py` | 创建 | 考试管理服务 |
| 3 | `backend/app/schemas/exam.py` | 创建 | 考试请求/响应模型 |
| 4 | `backend/tests/test_exams_api.py` | 创建 | 考试 API 测试 |

## 详细要求

### backend/app/routers/exams.py
- `POST /api/exams`：创建考试
- `GET /api/exams`：考试列表（分页，按状态筛选）
- `GET /api/exams/:id`：考试详情（含题目列表）
- `PUT /api/exams/:id`：更新考试配置
- `DELETE /api/exams/:id`：删除考试
- `POST /api/exams/:id/publish`：发布考试（draft → open）
- `POST /api/exams/:id/close`：关闭考试（open → closed）

### backend/app/services/exam_service.py
- `create_exam(data, user_id)`：创建考试，关联题目
  - 验证 question_ids 是否存在
  - 计算 total_score（所有题目分值之和，或使用用户指定值）
  - 创建 exam_questions 关联
- `list_exams(status, page, page_size)`：分页列表
- `get_exam(exam_id)`：详情，含关联的题目列表
- `update_exam(exam_id, data)`：更新配置
- `delete_exam(exam_id)`：级联删除关联
- `publish_exam(exam_id)`：状态变更，验证至少有 1 题
- `close_exam(exam_id)`：状态变更

### backend/app/schemas/exam.py
- `ExamCreate`：title, description, duration_minutes, total_score, pass_score, question_ids(list)
- `ExamUpdate`：所有字段可选
- `ExamResponse`：id, title, description, duration_minutes, total_score, pass_score, status, question_count, created_at
- `ExamDetail`：ExamResponse + questions(list)
- `ExamListResponse`：items, total, page, page_size

### backend/tests/test_exams_api.py
- 创建考试成功
- 创建考试时 question_ids 不存在返回 400
- 考试列表分页
- 按状态筛选
- 考试详情含题目列表
- 更新考试配置
- 删除考试
- 发布考试（draft → open）
- 关闭考试（open → closed）
- 无题目时不能发布

## 验收标准
1. 创建考试可关联多个题目
2. 考试列表支持分页和状态筛选
3. 考试详情包含完整题目列表
4. 状态转换正确（draft → open → closed）
5. 删除考试级联删除关联
6. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_exams_api.py -v

# 手动测试
curl -X POST http://localhost:8000/api/exams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"测试考试","duration_minutes":60,"total_score":100,"pass_score":60,"question_ids":[1,2,3]}'
```
