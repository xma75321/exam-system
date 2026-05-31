# TASK-027：前端结果页面

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：5 小时
- **依赖**：TASK-025, TASK-026
- **前置条件**：评分功能已完成

## 任务描述
实现前端考试结果页面，显示成绩概览和逐题回顾。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/app/attempts/[id]/result/page.tsx` | 创建 | 结果页面 |
| 2 | `frontend/src/components/ScoreSummary.tsx` | 创建 | 成绩概览组件 |
| 3 | `frontend/src/components/QuestionReview.tsx` | 创建 | 逐题回顾组件 |
| 4 | `frontend/src/components/TypeStats.tsx` | 创建 | 题型统计组件 |

## 详细要求

### frontend/src/components/ScoreSummary.tsx
- 大号分数显示（如 "85.0 分"）
- 通过/未通过标签（绿色/红色）
- 满分和及格线
- 用时（分钟）
- 正确率（如 "42/50"）

### frontend/src/components/TypeStats.tsx
- 按题型显示统计：
  - 单选：18/20 正确
  - 多选：8/10 正确
  - 判断：10/10 正确
  - 填空：4/5 正确
  - 简答：待评分
- 每种题型用对应颜色标签

### frontend/src/components/QuestionReview.tsx
- 每题显示：
  - 题号 + 题型标签
  - 题目内容
  - 用户答案
  - 正确答案
  - 对错标记（绿色对号 / 红色叉号）
  - 得分 / 满分
  - 解析（如果有）
- 选择题高亮正确和错误选项
- 简答题显示 "待评分" 状态

### frontend/src/app/attempts/[id]/result/page.tsx
- 顶部：ScoreSummary
- 中部：TypeStats
- 下部：QuestionReview 列表
- 底部：返回考试列表按钮

## 验收标准
1. 结果页正确显示总分
2. 通过/未通过标签正确
3. 题型统计正确
4. 逐题回顾显示用户答案和正确答案
5. 对错标记正确
6. 解析正确显示
7. 简答题显示待评分状态

## 测试方法
```bash
cd frontend
npm run dev
# 1. 完成一次考试并提交
# 2. 验证结果页显示正确
# 3. 检查分数、正确率
# 4. 检查逐题回顾
# 5. 验证简答题待评分状态
```
