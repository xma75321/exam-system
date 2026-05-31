# TASK-017：前端题库页面

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：4 小时
- **依赖**：TASK-016, TASK-014
- **前置条件**：前端上传页面完成，题库查询 API 可用

## 任务描述
实现前端题库管理页面，支持题目列表展示、题型筛选和题目详情查看。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/src/app/questions/page.tsx` | 创建 | 题库页面 |
| 2 | `frontend/src/components/QuestionCard.tsx` | 创建 | 题目卡片组件 |
| 3 | `frontend/src/components/QuestionFilter.tsx` | 创建 | 筛选栏组件 |
| 4 | `frontend/src/components/Pagination.tsx` | 创建 | 分页组件 |

## 详细要求

### frontend/src/components/QuestionFilter.tsx
- 题型下拉选择：全部 / 单选 / 多选 / 判断 / 填空 / 简答
- 搜索框（按题目内容搜索，可选）
- 切换筛选条件时自动刷新列表

### frontend/src/components/QuestionCard.tsx
- 折叠状态：题号、题型标签（颜色区分）、内容摘要（前 60 字）、分值
- 展开状态：完整题目内容、选项列表（选择题）、正确答案、解析
- 点击展开/收起
- 题型标签颜色：
  - 单选：蓝色
  - 多选：紫色
  - 判断：绿色
  - 填空：橙色
  - 简答：灰色

### frontend/src/components/Pagination.tsx
- 上一页 / 下一页按钮
- 页码显示（当前页高亮）
- 总页数显示
- 每页条数选择（10/20/50）

### frontend/src/app/questions/page.tsx
- 顶部筛选栏
- 题目卡片列表
- 底部分页
- 空状态提示（"暂无题目，去上传试卷吧"）
- 加载状态骨架屏

## 验收标准
1. 访问 `/questions` 显示题目列表
2. 题型筛选正确过滤题目
3. 分页功能正常
4. 点击题目卡片可展开查看详情
5. 选项、答案、解析正确显示
6. 空状态显示友好提示
7. 加载中显示骨架屏

## 测试方法
```bash
cd frontend
npm run dev
# 1. 访问 http://localhost:3000/questions
# 2. 验证题目列表正确显示
# 3. 切换题型筛选
# 4. 翻页
# 5. 展开/收起题目详情
```
