# TASK-021：前端答题页面

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：8 小时
- **依赖**：TASK-019, TASK-020
- **前置条件**：考试列表页面和答题 API 已完成

## 任务描述
实现前端在线答题页面，包含题目展示、作答、题号导航和提交功能。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/app/exams/[id]/take/page.tsx` | 创建 | 答题页面 |
| 2 | `frontend/src/components/QuestionDisplay.tsx` | 创建 | 题目展示组件 |
| 3 | `frontend/src/components/QuestionNav.tsx` | 创建 | 题号导航组件 |
| 4 | `frontend/src/components/AnswerInput.tsx` | 创建 | 答题输入组件 |

## 详细要求

### frontend/src/components/AnswerInput.tsx
按题型提供不同的输入控件：
- 单选题：Radio 按钮组（A/B/C/D）
- 多选题：Checkbox 组
- 判断题：Radio 按钮（正确/错误）
- 填空题：文本输入框
- 简答题：多行文本框

### frontend/src/components/QuestionDisplay.tsx
- 题号 + 题型标签
- 题目内容（富文本）
- 选项列表（选择题）
- 答题输入区
- 分值显示

### frontend/src/components/QuestionNav.tsx
- 侧栏题号网格
- 题号状态：
  - 当前题：蓝色高亮边框
  - 已答：绿色背景
  - 未答：白色背景
- 点击跳转到对应题目
- 进度显示：已答 / 总数
- 提交按钮（底部）

### frontend/src/app/exams/[id]/take/page.tsx
- 左右布局：左侧答题区，右侧导航+计时器
- 首次加载：调用开始考试 API
- 切题：自动保存当前答案
- 提交：确认弹窗 → 调用提交 API → 跳转结果页

## 验收标准
1. 访问考试答题页正确加载题目
2. 单选题显示 Radio 按钮
3. 多选题显示 Checkbox
4. 判断题显示正确/错误选项
5. 填空题显示文本框
6. 简答题显示多行文本框
7. 选择答案后题号变绿
8. 点击题号可跳转
9. 提交后跳转到结果页

## 测试方法
```bash
cd frontend
npm run dev
# 1. 创建一个开放中的考试
# 2. 在考试列表点击"开始考试"
# 3. 逐一作答
# 4. 验证题号颜色变化
# 5. 提交考试
# 6. 验证跳转到结果页
```
