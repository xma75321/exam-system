# TASK-028：统计页面与全局异常处理

## 基本信息
- **Sprint**：Sprint 2
- **预估工时**：4 小时
- **依赖**：TASK-027
- **前置条件**：结果页面已完成

## 任务描述
实现统计分析页面（概览 + 趋势图）和前后端全局异常处理。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/routers/reports.py` | 创建 | 统计 API 路由 |
| 2 | `frontend/src/app/reports/page.tsx` | 创建 | 统计页面 |
| 3 | `frontend/src/components/TrendChart.tsx` | 创建 | 成绩趋势图表 |
| 4 | `frontend/src/components/GlobalErrorBoundary.tsx` | 创建 | 前端错误边界 |
| 5 | `backend/app/utils/exceptions.py` | 创建 | 后端异常处理 |

## 详细要求

### backend/app/routers/reports.py
- `GET /api/reports/overview`：
  - 统计当前用户的：考试次数、平均分、最高分、通过率
  - 通过 = total_score ≥ pass_score

- `GET /api/reports/trend?days=30`：
  - 返回最近 N 天的成绩记录
  - 按时间排序
  - 每条：日期、分数、考试标题

### frontend/src/components/TrendChart.tsx
- 使用 recharts 折线图
- X 轴：日期
- Y 轴：分数
- 及格线参考线
- 鼠标悬停显示详细信息

### frontend/src/app/reports/page.tsx
- 顶部：统计卡片（考试次数、平均分、最高分、通过率）
- 中部：趋势折线图
- 时间范围选择（7天/30天/全部）
- 空状态：暂无考试记录

### backend/app/utils/exceptions.py
- 全局异常处理器
- 自定义异常类：
  - `NotFoundException`：资源不存在 → 404
  - `BadRequestException`：请求错误 → 400
  - `UnauthorizedException`：未认证 → 401
  - `ForbiddenException`：无权限 → 403
- 全局 catch：未捕获异常 → 500 + 日志记录

### frontend/src/components/GlobalErrorBoundary.tsx
- React Error Boundary
- 捕获子组件渲染异常
- 显示友好的错误页面
- "刷新重试" 按钮
- 开发环境显示错误详情

## 验收标准
1. 统计 API 返回正确的概览数据
2. 趋势 API 返回最近 N 天的成绩
3. 统计页面正确渲染数据
4. 折线图正确显示趋势
5. 及格参考线显示
6. 后端异常返回标准格式 JSON
7. 前端异常显示友好错误页面

## 测试方法
```bash
# 后端
cd backend
pytest tests/ -v

# 前端
cd frontend
npm run dev
# 1. 访问 /reports
# 2. 验证统计卡片显示
# 3. 验证折线图渲染
# 4. 触发一个异常，验证错误边界
```
