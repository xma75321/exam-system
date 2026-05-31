# CLAUDE.md — 智能考试系统 Claude Code 指南

## 项目信息

- **项目名称**：智能考试系统（MVP）
- **项目目录**：`E:/Ai-project/`
- **技术栈**：Next.js + TypeScript + Tailwind | FastAPI + SQLAlchemy + Alembic | MySQL 8
- **文档语言**：中文

## 快速参考

参见 `AGENTS.md` 获取完整的项目结构、代码规范、开发命令和 API 设计约定。

## 核心约定

1. **语言**：文档和注释用中文，代码标识符用英文
2. **每个 TASK ≤ 5 个文件**
3. **每个 TASK 独立可测试**
4. **后端先行**：先建数据模型和 API，再做前端
5. **API 驱动**：前后端通过 REST API 解耦

## 关键路径

| 用途 | 路径 |
|------|------|
| 后端入口 | `backend/app/main.py` |
| 数据库模型 | `backend/app/models/` |
| API 路由 | `backend/app/routers/` |
| 数据库迁移 | `backend/alembic/versions/` |
| 前端页面 | `frontend/src/app/` |
| 前端组件 | `frontend/src/components/` |
| API 客户端 | `frontend/src/lib/api.ts` |
| 任务定义 | `tasks/TASK-XXX.md` |
| 产品规格 | `specs/SPEC.md` |
| Sprint 计划 | `sprints/SPRINT-PLAN.md` |

## TASK 执行要求

1. 读取 `tasks/TASK-XXX.md` 获取任务详情
2. 按文件清单创建/修改文件（≤ 5 个文件）
3. 运行指定的测试方法
4. 逐条验证验收标准
5. 提交代码：`feat(TASK-XXX): 简要描述`

## 产品核心流程

```
上传 Word → 解析题目 → 题库管理 → 创建考试 → 在线答题 → 自动评分 → 成绩报告
```

## 题型支持

| 题型代码 | 中文名 | 自动评分 |
|----------|--------|----------|
| single | 单选题 | 是 |
| multi | 多选题 | 是 |
| judge | 判断题 | 是 |
| fill | 填空题 | 是 |
| essay | 简答题 | 否（预留接口） |
