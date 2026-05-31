# TASK-003：数据库设计与迁移

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：4 小时
- **依赖**：TASK-001
- **前置条件**：后端项目初始化完成，MySQL 8 已运行

## 任务描述
创建所有 SQLAlchemy 数据库模型，配置 Alembic 迁移工具，生成初始迁移。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `backend/app/models/__init__.py` | 创建 | 模型导出 |
| 2 | `backend/app/models/user.py` | 创建 | User 模型 |
| 3 | `backend/app/models/exam.py` | 创建 | Exam、Question、Option 模型 |
| 4 | `backend/app/models/attempt.py` | 创建 | ExamAttempt、QuestionResponse 模型 |
| 5 | `backend/alembic.ini` | 创建 | Alembic 配置 |

## 详细要求

### backend/app/models/user.py
User 模型字段：
- id: Integer, PK, auto_increment
- username: String(50), unique, not null
- email: String(100), unique, not null
- password_hash: String(255), not null
- created_at: DateTime, default now

### backend/app/models/exam.py
Exam 模型字段：
- id, title(String 200), description(Text), duration_minutes(Integer), total_score(Numeric 5,1), pass_score(Numeric 5,1), status(Enum: draft/open/closed), created_by(FK→users), created_at

Question 模型字段：
- id, exam_id(FK→exams), type(Enum: single/multi/judge/fill/essay), content(Text), answer(Text), score(Numeric 5,1), explanation(Text nullable), sort_order(Integer)

Option 模型字段：
- id, question_id(FK→questions), label(String 5), content(Text), is_correct(Boolean)

关系：
- Exam → Questions (one-to-many, cascade delete)
- Question → Options (one-to-many, cascade delete)

### backend/app/models/attempt.py
ExamAttempt 模型字段：
- id, exam_id(FK→exams), user_id(FK→users), started_at(DateTime), submitted_at(DateTime nullable), status(Enum: in_progress/submitted/graded), total_score(Numeric 5,1 nullable), objective_score(Numeric 5,1 nullable), subjective_score(Numeric 5,1 nullable)

QuestionResponse 模型字段：
- id, attempt_id(FK→exam_attempts), question_id(FK→questions), user_answer(Text nullable), is_correct(Boolean nullable), score(Numeric 5,1 nullable), graded_by(Enum: auto/manual/pending)

### backend/alembic.ini
- sqlalchemy.url 从环境变量读取
- 配置 script_location

## 验收标准
1. 运行 `alembic revision --autogenerate -m "初始表结构"` 成功生成迁移文件
2. 运行 `alembic upgrade head` 成功创建所有表
3. MySQL 中可看到 users、exams、questions、options、exam_attempts、question_responses 共 6 张表
4. 表结构字段类型、约束、外键关系正确
5. `alembic downgrade -1` 可回滚

## 测试方法
```bash
cd backend
# 确保 MySQL 运行且 .env 中 DATABASE_URL 正确
alembic revision --autogenerate -m "初始表结构"
alembic upgrade head

# 验证表已创建
mysql -u root -e "USE exam_system; SHOW TABLES;"
# 预期：users, exams, questions, options, exam_attempts, question_responses
```
