# TASK-025：客观题自动评分

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：5 小时
- **依赖**：TASK-024
- **前置条件**：答题提交流程已完成

## 任务描述
实现客观题（单选、多选、判断、填空）的自动评分逻辑。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/services/grade_service.py` | 创建 | 评分服务 |
| 2 | `backend/app/routers/grade.py` | 创建 | 评分路由 |
| 3 | `backend/tests/test_grade_service.py` | 创建 | 评分测试 |

## 详细要求

### backend/app/services/grade_service.py
- `grade_attempt(attempt_id: int)`：主入口
  - 获取 attempt 和所有 responses
  - 遍历每道题，按题型调用对应评分函数
  - 单选题、多选题、判断题、填空题自动评分
  - 简答题标记为 pending（预留接口）
  - 计算总分、客观题得分
  - 更新 attempt 状态为 graded

- `grade_single_choice(response, question)`：
  - 用户答案与正确答案完全匹配 → 得满分
  - 否则 → 0 分

- `grade_multi_choice(response, question)`：
  - 用户答案与正确答案完全匹配 → 得满分
  - 否则 → 0 分（全对才得分，漏选/多选均不得分）

- `grade_judge(response, question)`：
  - 完全匹配 → 得满分
  - 否则 → 0 分

- `grade_fill(response, question)`：
  - 去除首尾空格后匹配
  - 不区分大小写
  - 多空题：每个空分别评分
  - 完全匹配 → 得满分

- `grade_essay(response, question)`：
  - 标记 graded_by = "pending"
  - score = null

### backend/app/routers/grade.py
- `POST /api/attempts/:id/grade`：手动触发评分
- 提交 API 内部也自动调用评分

### backend/tests/test_grade_service.py
- 单选题正确/错误评分
- 多选题全对/漏选/多选评分
- 判断题正确/错误评分
- 填空题大小写不敏感评分
- 简答题 pending 状态
- 混合题型评分总分计算
- 重复评分处理

## 验收标准
1. 单选题答对得满分，答错得 0 分
2. 多选题全对得满分，否则 0 分
3. 判断题答对得满分，答错得 0 分
4. 填空题忽略大小写和空格
5. 简答题标记为 pending
6. 总分正确计算
7. attempt 状态变为 graded
8. 所有测试用例通过

## 测试方法
```bash
cd backend
pytest tests/test_grade_service.py -v

# 手动测试：提交考试后自动评分
curl -X POST http://localhost:8000/api/attempts/1/grade \
  -H "Authorization: Bearer $TOKEN"
# 预期：返回评分结果
```
