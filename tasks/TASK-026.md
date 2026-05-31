# TASK-026：主观题评分接口

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：2 小时
- **依赖**：TASK-025
- **前置条件**：客观题自动评分已完成

## 任务描述
实现主观题（简答题）人工评分接口，预留评分功能但 MVP 不实现自动评分。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/routers/grade.py` | 修改 | 添加手动评分端点 |
| 2 | `backend/app/services/grade_service.py` | 修改 | 添加手动评分方法 |
| 3 | `backend/app/schemas/grade.py` | 创建 | 评分请求/响应模型 |
| 4 | `backend/tests/test_manual_grade.py` | 创建 | 手动评分测试 |

## 详细要求

### backend/app/schemas/grade.py
- `ManualGradeRequest`：score(float), comment(str optional)
- `GradeResult`：total_score, objective_score, subjective_score, correct_count, total_count

### backend/app/routers/grade.py（修改）
- `PUT /api/responses/:id/score`：手动评分
  - 验证 response 属于当前用户
  - 验证 question 类型为 essay
  - 验证 score ≤ 题目分值
  - 更新 response 的 score 和 graded_by = "manual"
  - 重新计算 attempt 总分

### backend/app/services/grade_service.py（修改）
- `manual_grade(response_id, score, comment)`：
  - 更新 response
  - 重新计算 attempt 的 subjective_score 和 total_score
  - 如果所有 response 都已评分，更新 attempt 状态

### backend/tests/test_manual_grade.py
- 手动评分简答题成功
- 分值超过上限返回 400
- 非简答题不能手动评分
- 评分后总分重新计算
- 非本人的 response 不能评分

## 验收标准
1. `PUT /api/responses/:id/score` 可手动评分简答题
2. 分值校验正确
3. 评分后 attempt 总分更新
4. 非简答题不能使用该接口
5. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_manual_grade.py -v
```
