# TASK-014：题库查询 API

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：3 小时
- **依赖**：TASK-013
- **前置条件**：题目可入库

## 任务描述
实现题库查询接口，支持分页、题型筛选和题目详情查看。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/routers/questions.py` | 创建 | 题库路由 |
| 2 | `backend/app/services/question_service.py` | 修改 | 添加查询方法 |
| 3 | `backend/app/schemas/question.py` | 修改 | 添加查询响应模型 |
| 4 | `backend/tests/test_questions_api.py` | 创建 | 题库 API 测试 |

## 详细要求

### backend/app/routers/questions.py
- `GET /api/questions`：题目列表
  - 查询参数：type(可选), page(默认1), page_size(默认20)
  - 返回分页结果
- `GET /api/questions/:id`：题目详情
  - 返回题目完整信息（含选项、答案、解析）
- `DELETE /api/questions/:id`：删除题目
  - 级联删除 options

### backend/app/services/question_service.py（修改）
- `list_questions(type: str, page: int, page_size: int)`：
  - 按题型筛选
  - 按创建时间倒序
  - 返回 (items, total)
- `get_question(question_id: int)`：获取单个题目详情
- `delete_question(question_id: int)`：删除题目

### backend/app/schemas/question.py（修改）
- `QuestionListItem`：id, type, content(前100字), score, created_at
- `QuestionDetail`：id, type, content, options(list), answer, score, explanation, created_at
- `QuestionListResponse`：items, total, page, page_size

### backend/tests/test_questions_api.py
- 获取题目列表（无筛选）
- 按题型筛选
- 分页功能
- 获取题目详情（含选项）
- 删除题目
- 查询不存在的题目返回 404

## 验收标准
1. `GET /api/questions` 返回分页题目列表
2. `?type=single` 正确筛选单选题
3. 分页参数正确工作
4. `GET /api/questions/:id` 返回含选项的完整详情
5. `DELETE /api/questions/:id` 成功删除
6. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_questions_api.py -v

# 手动测试
curl "http://localhost:8000/api/questions?page=1&page_size=10&type=single" \
  -H "Authorization: Bearer $TOKEN"
```
