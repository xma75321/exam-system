# AGENTS.md — 智能考试系统 AI Agent 协作规范

## 项目概述

智能考试系统（MVP）：上传 Word 试卷 → 自动解析 → 生成考试 → 在线答题 → 自动评分 → 成绩报告。

**技术栈**：Next.js + TypeScript + Tailwind（前端）| FastAPI + SQLAlchemy + Alembic（后端）| MySQL 8（数据库）

**产品模式**：自测模式，无角色区分，所有用户可上传试卷并参加考试。

---

## 通用规则

### 语言
- 所有文档、注释、提交信息使用**中文**
- 代码标识符（变量名、函数名、类名）使用**英文**
- API 路径使用**英文**

### 代码规范
- **Python**：PEP 8，使用 `ruff` 格式化，`mypy` 类型检查
- **TypeScript**：ESLint + Prettier，严格模式 (`strict: true`)
- **命名**：Python 用 `snake_case`，TypeScript 用 `camelCase`（变量/函数）、`PascalCase`（组件/类型）
- **文件命名**：Python 用 `snake_case.py`，TypeScript 组件用 `PascalCase.tsx`，工具用 `camelCase.ts`

### Git 规范
- 每个 TASK 完成后提交一次
- 提交信息格式：`feat(TASK-XXX): 简要描述` 或 `fix(TASK-XXX): 简要描述`
- 不要提交 `.env`、`node_modules`、`__pycache__`、`uploads/` 目录

---

## 项目结构

```
E:/Ai-project/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库连接
│   │   ├── models/             # SQLAlchemy 模型
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── routers/            # API 路由
│   │   ├── services/           # 业务逻辑
│   │   └── utils/              # 工具函数
│   ├── alembic/                # 数据库迁移
│   ├── tests/                  # 后端测试
│   ├── uploads/                # 上传文件存储（.gitignore）
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/                   # Next.js 前端
│   ├── src/
│   │   ├── app/                # App Router 页面
│   │   ├── components/         # UI 组件
│   │   ├── hooks/              # 自定义 Hooks
│   │   ├── lib/                # 工具库（API 客户端等）
│   │   ├── types/              # TypeScript 类型定义
│   │   └── styles/             # 全局样式
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── docs/                       # 项目文档
├── specs/                      # 产品规格
├── sprints/                    # Sprint 计划
├── tasks/                      # 任务定义
├── AGENTS.md                   # 本文件
└── CLAUDE.md                   # Claude Code 指南
```

---

## 约束

### 绝对禁止
- 不修改 `tasks/` 目录下的任务定义文件
- 不在代码中硬编码密码、密钥或数据库连接串
- 不使用 `any` 类型（TypeScript）
- 不跳过 Alembic 迁移直接修改数据库
- 不在未完成的 TASK 上开始下一个 TASK

### 必须遵守
- 每个 TASK 修改的文件数 ≤ 5
- 每个 TASK 完成后必须通过其验收标准
- 所有 API 端点必须有 Pydantic 请求/响应模型
- 所有数据库变更必须通过 Alembic 迁移
- 前端组件必须有 TypeScript 类型定义

---

## 开发命令

### 后端
```bash
# 安装依赖
cd backend && pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 运行开发服务器
uvicorn app.main:app --reload --port 8000

# 运行测试
pytest tests/ -v

# 类型检查
mypy app/

# 代码格式化
ruff check app/ --fix
```

### 前端
```bash
# 安装依赖
cd frontend && npm install

# 运行开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码检查
npm run lint

# 运行测试
npm run test

# 构建
npm run build
```

### 数据库
```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

---

## TASK 执行流程

1. **读取任务文件**：`tasks/TASK-XXX.md`
2. **检查依赖**：确认所有前置 TASK 已完成
3. **执行任务**：按任务文件中的文件清单创建/修改文件
4. **运行测试**：执行任务文件中指定的测试方法
5. **验证验收标准**：逐条确认验收标准通过
6. **提交代码**：`git add` + `git commit`
7. **标记完成**：在任务跟踪中标记 TASK 完成

---

## API 设计约定

- 所有 API 以 `/api` 为前缀
- 使用 RESTful 风格
- 成功响应：`{"code": 0, "data": {...}, "message": "success"}`
- 错误响应：`{"code": 错误码, "data": null, "message": "错误描述"}`
- 分页参数：`?page=1&page_size=20`
- 分页响应：`{"items": [...], "total": 100, "page": 1, "page_size": 20}`

### 错误码
| 错误码 | 含义 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

---

## 前端约定

- 使用 App Router（`src/app/`）
- 页面组件在 `src/app/` 对应路由目录下
- 通用组件在 `src/components/`
- API 请求统一通过 `src/lib/api.ts` 封装
- 状态管理：优先使用 React Context，复杂状态使用 Zustand
- 样式：Tailwind CSS，不写自定义 CSS
- 表单处理：React Hook Form + Zod 验证
