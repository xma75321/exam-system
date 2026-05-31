# TASK-019：前端考试列表页面

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：3 小时
- **依赖**：TASK-018, TASK-015
- **前置条件**：考试创建页面完成

## 任务描述
实现前端考试列表页面，展示所有考试及其状态，支持操作和状态筛选。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/app/exams/page.tsx` | 创建 | 考试列表页面 |
| 2 | `frontend/src/components/ExamCard.tsx` | 创建 | 考试卡片组件 |
| 3 | `frontend/src/components/StatusBadge.tsx` | 创建 | 状态标签组件 |

## 详细要求

### frontend/src/components/StatusBadge.tsx
- 草稿（draft）：灰色标签
- 开放中（open）：绿色标签
- 已关闭（closed）：红色标签

### frontend/src/components/ExamCard.tsx
- 考试标题
- 状态标签
- 题数 / 满分 / 时长
- 创建时间
- 操作按钮：
  - 草稿：查看、编辑、发布、删除
  - 开放中：查看、开始考试、关闭
  - 已关闭：查看、删除

### frontend/src/app/exams/page.tsx
- 顶部：筛选栏（按状态）+ "创建考试" 按钮
- 卡片网格布局（响应式）
- 分页
- 空状态提示
- 操作确认弹窗（删除、关闭）

## 验收标准
1. 访问 `/exams` 显示考试列表
2. 状态筛选正确过滤
3. 卡片显示完整信息
4. 状态标签颜色正确
5. 操作按钮与状态匹配
6. 删除操作有确认弹窗
7. 点击"开始考试"跳转到答题页

## 测试方法
```bash
cd frontend
npm run dev
# 1. 访问 http://localhost:3000/exams
# 2. 验证考试卡片正确显示
# 3. 测试状态筛选
# 4. 测试各操作按钮
```
