# OpenCode 执行指令

请严格按照以下指令执行智能考试系统 MVP 的开发工作。

---

## 第一步：阅读规划文档（必须先读）

按顺序读取以下文件，理解项目全貌：

```
1. E:/Ai-project/AGENTS.md          — 项目结构、代码规范、开发命令
2. E:/Ai-project/CLAUDE.md          — 快速参考、关键路径
3. E:/Ai-project/specs/SPEC.md      — 完整产品规格（数据模型、API、前端页面）
4. E:/Ai-project/sprints/SPRINT-PLAN.md — Sprint 计划和依赖关系
```

读完后，你必须理解以下内容：
- 技术栈：Next.js + TypeScript + Tailwind（前端），FastAPI + SQLAlchemy + Alembic（后端），MySQL 8
- 核心流程：上传 Word → 解析题目 → 题库管理 → 创建考试 → 在线答题 → 自动评分 → 成绩报告
- 文档和注释用中文，代码标识符用英文
- API 路径以 `/api` 为前缀

---

## 第二步：按顺序执行任务

依次执行 `E:/Ai-project/tasks/` 目录下的 TASK-001.md 到 TASK-028.md。

### 每个任务的执行流程

```
1. 读取 tasks/TASK-XXX.md
2. 检查依赖是否已完成（看任务文件中的"依赖"字段）
3. 按文件清单创建/修改文件（严格控制在 ≤ 5 个文件内）
4. 运行任务中指定的测试方法
5. 逐条验证验收标准
6. 只有验收标准全部通过后，才继续下一个任务
```

### 绝对约束

- **不跳过任何任务**，按 001 → 028 顺序执行
- **每个任务 ≤ 5 个文件**，不超范围
- **验收标准不通过则不继续**，必须修复后才进入下一任务
- **数据库变更必须通过 Alembic 迁移**，不直接改数据库
- **不使用 any 类型**（TypeScript）
- **不硬编码密码、密钥、数据库连接串**
- **文件名和目录结构严格按 AGENTS.md 中的规范**

---

## 第三步：处理任务依赖

任务之间有依赖关系，关键依赖链：

```
001 → 003 → 004 → 005 → 006    （后端基础 + 认证）
002                              （前端初始化，可与 001 并行）
007 → 008 → 009/010/011/012      （Word 解析）
013 → 014 → 015                  （题库 + 考试 API）
016 → 017 → 018 → 019            （前端页面）
020 → 021 → 022/023 → 024        （答题流程）
025 → 026 → 027 → 028            （评分 + 报告）
```

- TASK-002（前端初始化）可与 TASK-001（后端初始化）并行执行
- 其他任务严格按依赖顺序

---

## 第四步：环境准备（执行任务前）

### 后端环境
```bash
# 确认 Python 可用
python --version   # 需要 3.11+

# 确认 MySQL 运行
mysql --version    # 需要 8.0+
```

### 前端环境
```bash
# 确认 Node.js 可用
node --version     # 需要 18+
npm --version
```

### 如果环境不满足，先安装再继续

---

## 第五步：验证里程碑

### Sprint 1 完成后（TASK-015 完成后）验证：
```bash
# 后端启动
cd E:/Ai-project/backend
uvicorn app.main:app --reload --port 8000

# 健康检查
curl http://localhost:8000/health

# 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"123456"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'

# 上传文件
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.docx"

# 查询题目
curl http://localhost:8000/api/questions \
  -H "Authorization: Bearer $TOKEN"

# 创建考试
curl -X POST http://localhost:8000/api/exams \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"测试","duration_minutes":60,"total_score":100,"pass_score":60,"question_ids":[1]}'
```

### Sprint 2 完成后（TASK-028 完成后）验证：
```bash
# 前端启动
cd E:/Ai-project/frontend
npm run dev

# 浏览器完整流程测试：
# 1. 访问 http://localhost:3000/auth → 注册 → 登录
# 2. 访问 /upload → 上传 Word → 确认入库
# 3. 访问 /questions → 查看题库
# 4. 访问 /exams/new → 创建考试
# 5. 访问 /exams → 开始考试
# 6. 答题 → 提交 → 查看结果
# 7. 访问 /reports → 查看统计
```

---

## 第六步：完成后输出

所有 28 个任务完成后，请输出：

1. **完成状态表**：每个 TASK 的完成状态
2. **文件清单**：实际创建的所有文件路径
3. **已知问题**：如果有未解决的问题，列出
4. **启动说明**：如何启动前后端

---

## 补充说明

### Word 测试试卷格式

在执行 TASK-008 时，需要创建一个测试用的 .docx 文件。请使用 python-docx 生成，格式参考 `specs/SPEC.md` 第 7 节。

### 数据库配置

确保 `.env` 文件中 `DATABASE_URL` 指向已创建的 MySQL 数据库：
```
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/exam_system
```

先创建数据库：
```sql
CREATE DATABASE exam_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 错误处理

如果某个任务执行失败：
1. 不要跳过，修复后继续
2. 如果是环境问题（MySQL 未运行等），先解决环境
3. 如果是任务定义不清，按 `specs/SPEC.md` 中的规格为准
