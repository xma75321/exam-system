# TASK-018：前端考试创建页面

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：6 小时
- **依赖**：TASK-017, TASK-015
- **前置条件**：题库页面完成，考试管理 API 可用

## 任务描述
实现前端考试创建页面，支持设置考试参数和从题库选择题目。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/app/exams/new/page.tsx` | 创建 | 创建考试页面 |
| 2 | `frontend/src/components/ExamForm.tsx` | 创建 | 考试配置表单 |
| 3 | `frontend/src/components/QuestionSelector.tsx` | 创建 | 题目选择器 |
| 4 | `frontend/src/components/SelectedQuestions.tsx` | 创建 | 已选题目列表 |

## 详细要求

### frontend/src/components/ExamForm.tsx
- 表单字段：
  - 考试标题（必填，1-200 字符）
  - 描述（选填）
  - 时长（必填，数字，5-300 分钟）
  - 满分（必填，数字，1-1000）
  - 及格分（必填，数字，≤ 满分）
- 使用 react-hook-form + zod 验证
- "保存草稿" 和 "发布考试" 两个按钮

### frontend/src/components/QuestionSelector.tsx
- 左侧区域
- 题库列表（从 API 加载）
- 题型筛选
- 勾选题目
- 每题显示：题型标签、内容摘要、分值
- 已选题目不可重复勾选
- 支持全选/取消全选

### frontend/src/components/SelectedQuestions.tsx
- 右侧区域
- 已选题目列表
- 可拖拽排序（或上下箭头调整顺序）
- 可修改每题分值
- 可移除已选题目
- 显示已选题数和总分
- 总分实时更新

### frontend/src/app/exams/new/page.tsx
- 上下布局：上方表单，下方选题区
- 选题区左右分栏：左侧选择，右侧已选
- 提交时验证：至少选择 1 题
- 创建成功后跳转到考试列表

## 验收标准
1. 访问 `/exams/new` 显示创建页面
2. 表单验证正确工作
3. 可从题库勾选题目
4. 已选题目可调整顺序
5. 可修改每题分值
6. 总分实时计算
7. 保存草稿成功
8. 发布考试成功（状态为 open）

## 测试方法
```bash
cd frontend
npm run dev
# 1. 访问 http://localhost:3000/exams/new
# 2. 填写考试信息
# 3. 从题库选择 5-10 道题
# 4. 调整题目顺序和分值
# 5. 点击"发布考试"
# 6. 验证跳转到考试列表，新考试显示在列表中
```
