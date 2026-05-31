# 智能考试系统（MVP）— 产品规格文档

## 1. 概述

### 1.1 产品定位
智能考试系统 MVP 版本，支持用户上传 Word 试卷，系统自动解析题目，在线组织考试，客观题自动评分，并生成成绩报告。

### 1.2 目标用户
- 需要自测的学习者
- 需要快速组卷的教师（无角色区分，所有用户功能一致）

### 1.3 核心价值
- 从 Word 试卷到在线考试的全自动化流程
- 即时评分反馈
- 学习数据追踪

---

## 2. 功能需求

### 2.1 用户管理（FR-AUTH）

| 编号 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| FR-AUTH-01 | 用户注册 | P0 | 用户名 + 邮箱 + 密码注册 |
| FR-AUTH-02 | 用户登录 | P0 | 用户名/邮箱 + 密码登录，返回 JWT |
| FR-AUTH-03 | 获取当前用户 | P0 | 通过 JWT 获取用户信息 |
| FR-AUTH-04 | 用户登出 | P1 | 前端清除 Token |

### 2.2 试卷解析（FR-PARSE）

| 编号 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| FR-PARSE-01 | 上传 Word 文件 | P0 | 支持 .docx 格式，最大 10MB |
| FR-PARSE-02 | 解析单选题 | P0 | 提取题干、选项、正确答案 |
| FR-PARSE-03 | 解析多选题 | P0 | 提取题干、选项、多个正确答案 |
| FR-PARSE-04 | 解析判断题 | P0 | 提取题干、正确/错误 |
| FR-PARSE-05 | 解析填空题 | P0 | 提取题干、填空答案 |
| FR-PARSE-06 | 解析简答题 | P0 | 提取题干、参考答案 |
| FR-PARSE-07 | 解析预览 | P0 | 返回结构化 JSON 供用户确认 |
| FR-PARSE-08 | 确认入库 | P0 | 用户确认后将题目存入题库 |

### 2.3 题库管理（FR-QB）

| 编号 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| FR-QB-01 | 题目列表 | P0 | 分页展示，支持按题型筛选 |
| FR-QB-02 | 题目详情 | P0 | 查看题目内容、选项、答案、解析 |
| FR-QB-03 | 删除题目 | P1 | 单个删除 |

### 2.4 考试管理（FR-EXAM）

| 编号 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| FR-EXAM-01 | 创建考试 | P0 | 设置标题、时长、及格分、选择题目 |
| FR-EXAM-02 | 考试列表 | P0 | 展示所有考试及状态 |
| FR-EXAM-03 | 考试详情 | P0 | 查看考试配置和题目列表 |
| FR-EXAM-04 | 更新考试 | P1 | 修改考试配置 |
| FR-EXAM-05 | 删除考试 | P1 | 删除考试及其关联数据 |
| FR-EXAM-06 | 发布考试 | P0 | 将草稿状态改为开放 |
| FR-EXAM-07 | 关闭考试 | P1 | 将开放状态改为关闭 |

### 2.5 在线答题（FR-TAKE）

| 编号 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| FR-TAKE-01 | 开始考试 | P0 | 创建答题记录，开始计时 |
| FR-TAKE-02 | 答题界面 | P0 | 按题型展示题目，支持作答 |
| FR-TAKE-03 | 计时器 | P0 | 倒计时显示，时间到自动提交 |
| FR-TAKE-04 | 自动保存 | P0 | 每 30 秒自动保存答案 |
| FR-TAKE-05 | 手动保存 | P1 | 用户手动保存当前答案 |
| FR-TAKE-06 | 题目导航 | P0 | 上一题/下一题/跳转任意题 |
| FR-TAKE-07 | 提交考试 | P0 | 确认提交，结束答题 |
| FR-TAKE-08 | 答题进度 | P0 | 显示已答/未答/总题数 |

### 2.6 自动评分（FR-GRADE）

| 编号 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| FR-GRADE-01 | 单选题评分 | P0 | 答案完全匹配得分 |
| FR-GRADE-02 | 多选题评分 | P0 | 全对得满分，漏选/多选得 0 分 |
| FR-GRADE-03 | 判断题评分 | P0 | 答案匹配得分 |
| FR-GRADE-04 | 填空题评分 | P0 | 忽略空格后匹配得分 |
| FR-GRADE-05 | 简答题评分接口 | P1 | 预留接口，返回 pending 状态 |
| FR-GRADE-06 | 自动触发评分 | P0 | 提交考试后自动触发客观题评分 |

### 2.7 成绩报告（FR-REPORT）

| 编号 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| FR-REPORT-01 | 成绩详情 | P0 | 总分、各题得分、正确率 |
| FR-REPORT-02 | 逐题回顾 | P0 | 展示每题的用户答案和正确答案 |
| FR-REPORT-03 | 统计概览 | P1 | 考试次数、平均分、最高分、通过率 |
| FR-REPORT-04 | 成绩趋势 | P1 | 按时间展示成绩变化折线图 |

---

## 3. 非功能需求

### 3.1 性能
| 编号 | 需求 | 指标 |
|------|------|------|
| NFR-PERF-01 | API 响应时间 | 95% 请求 < 500ms |
| NFR-PERF-02 | Word 文件解析 | 100 题试卷 < 10 秒 |
| NFR-PERF-03 | 并发答题 | 支持 50 人同时在线 |
| NFR-PERF-04 | 前端首屏加载 | < 3 秒 |

### 3.2 安全
| 编号 | 需求 | 说明 |
|------|------|------|
| NFR-SEC-01 | 密码加密 | 使用 bcrypt 哈希 |
| NFR-SEC-02 | JWT 认证 | Token 有效期 24 小时 |
| NFR-SEC-03 | 文件上传验证 | 仅允许 .docx，校验文件头 |
| NFR-SEC-04 | SQL 注入防护 | 使用 SQLAlchemy ORM |
| NFR-SEC-05 | CORS 配置 | 仅允许前端域名 |

### 3.3 可靠性
| 编号 | 需求 | 说明 |
|------|------|------|
| NFR-REL-01 | 答案持久化 | 自动保存，刷新不丢失 |
| NFR-REL-02 | 计时器准确性 | 服务端校验时间，防篡改 |
| NFR-REL-03 | 文件存储 | 上传文件保存到磁盘，数据库记录路径 |

### 3.4 兼容性
| 编号 | 需求 | 说明 |
|------|------|------|
| NFR-COMP-01 | 浏览器 | Chrome 90+、Firefox 88+、Edge 90+ |
| NFR-COMP-02 | Word 格式 | 支持 .docx（Office 2007+） |
| NFR-COMP-03 | 响应式 | 支持 1280px+ 桌面端 |

---

## 4. 数据模型

### 4.1 ER 图（文字描述）

```
users 1 ──── N exams (created_by)
users 1 ──── N exam_attempts
exams 1 ──── N questions
questions 1 ──── N options
exam_attempts 1 ──── N question_responses
questions 1 ──── N question_responses
```

### 4.2 表结构

详见 `AGENTS.md` 中的数据模型章节（users、exams、questions、options、exam_attempts、question_responses 六张表）。

### 4.3 枚举值

**question.type**：
- `single` — 单选题
- `multi` — 多选题
- `judge` — 判断题
- `fill` — 填空题
- `essay` — 简答题

**exam.status**：
- `draft` — 草稿
- `open` — 开放中
- `closed` — 已关闭

**exam_attempts.status**：
- `in_progress` — 答题中
- `submitted` — 已提交
- `graded` — 已评分

**question_responses.graded_by**：
- `auto` — 自动评分
- `manual` — 人工评分
- `pending` — 待评分

---

## 5. API 设计

### 5.1 认证模块

#### POST /api/auth/register
请求：
```json
{
  "username": "string(3-50)",
  "email": "string(email格式)",
  "password": "string(6-20)"
}
```
响应：201
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2026-05-30T10:00:00"
  },
  "message": "注册成功"
}
```

#### POST /api/auth/login
请求：
```json
{
  "username": "string",
  "password": "string"
}
```
响应：200
```json
{
  "code": 0,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400
  },
  "message": "登录成功"
}
```

#### GET /api/auth/me
请求头：`Authorization: Bearer <token>`
响应：200
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  },
  "message": "success"
}
```

### 5.2 上传解析模块

#### POST /api/upload
请求：`multipart/form-data`，字段名 `file`，仅接受 `.docx`
响应：200
```json
{
  "code": 0,
  "data": {
    "filename": "exam.docx",
    "questions": [
      {
        "temp_id": "q_001",
        "type": "single",
        "content": "Python 是什么类型的语言？",
        "options": [
          {"label": "A", "content": "编译型"},
          {"label": "B", "content": "解释型"},
          {"label": "C", "content": "汇编型"},
          {"label": "D", "content": "机器语言"}
        ],
        "answer": "B",
        "score": 2.0,
        "explanation": "Python 是解释型语言"
      }
    ],
    "total_count": 50,
    "type_summary": {
      "single": 20,
      "multi": 10,
      "judge": 10,
      "fill": 5,
      "essay": 5
    }
  },
  "message": "解析成功"
}
```

#### POST /api/upload/confirm
请求：
```json
{
  "filename": "exam.docx",
  "questions": [
    {
      "temp_id": "q_001",
      "type": "single",
      "content": "Python 是什么类型的语言？",
      "options": [
        {"label": "A", "content": "编译型"},
        {"label": "B", "content": "解释型"}
      ],
      "answer": "B",
      "score": 2.0,
      "explanation": "Python 是解释型语言"
    }
  ]
}
```
响应：201，返回保存后的题目列表（含真实 ID）

### 5.3 题库模块

#### GET /api/questions
查询参数：`?type=single&page=1&page_size=20`
响应：200
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "type": "single",
        "content": "Python 是什么类型的语言？",
        "score": 2.0,
        "created_at": "2026-05-30T10:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20
  },
  "message": "success"
}
```

#### GET /api/questions/:id
响应：200，返回题目完整信息（含选项、答案、解析）

#### DELETE /api/questions/:id
响应：200，返回 `{"code": 0, "message": "删除成功"}`

### 5.4 考试模块

#### POST /api/exams
请求：
```json
{
  "title": "Python 基础测试",
  "description": "测试 Python 基础知识",
  "duration_minutes": 60,
  "total_score": 100.0,
  "pass_score": 60.0,
  "question_ids": [1, 2, 3, 4, 5]
}
```
响应：201，返回创建的考试信息

#### GET /api/exams
查询参数：`?status=open&page=1&page_size=10`
响应：200，返回考试列表

#### GET /api/exams/:id
响应：200，返回考试详情（含题目列表）

#### PUT /api/exams/:id
请求：同 POST，部分字段可选
响应：200，返回更新后的考试信息

#### DELETE /api/exams/:id
响应：200

#### POST /api/exams/:id/publish
响应：200，将 draft → open

#### POST /api/exams/:id/close
响应：200，将 open → closed

### 5.5 答题模块

#### POST /api/attempts
请求：
```json
{
  "exam_id": 1
}
```
响应：201
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "exam_id": 1,
    "status": "in_progress",
    "started_at": "2026-05-30T10:00:00",
    "end_time": "2026-05-30T11:00:00",
    "questions": [
      {
        "id": 1,
        "type": "single",
        "content": "Python 是什么类型的语言？",
        "options": [
          {"label": "A", "content": "编译型"},
          {"label": "B", "content": "解释型"}
        ],
        "score": 2.0
      }
    ]
  },
  "message": "考试开始"
}
```

#### GET /api/attempts/:id
响应：200，返回答题进度（含已保存的答案）

#### PUT /api/attempts/:id/answers
请求：
```json
{
  "answers": [
    {"question_id": 1, "user_answer": "B"},
    {"question_id": 2, "user_answer": "A,C"}
  ]
}
```
响应：200

#### POST /api/attempts/:id/submit
响应：200
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "status": "submitted",
    "submitted_at": "2026-05-30T10:45:00"
  },
  "message": "提交成功"
}
```

### 5.6 评分模块

#### POST /api/attempts/:id/grade
响应：200
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "status": "graded",
    "total_score": 85.0,
    "objective_score": 80.0,
    "subjective_score": null,
    "correct_count": 42,
    "total_count": 50
  },
  "message": "评分完成"
}
```

#### PUT /api/responses/:id/score
请求：
```json
{
  "score": 8.0,
  "comment": "回答较好，但缺少关键点"
}
```
响应：200

### 5.7 报告模块

#### GET /api/attempts/:id/result
响应：200
```json
{
  "code": 0,
  "data": {
    "exam_title": "Python 基础测试",
    "total_score": 85.0,
    "pass_score": 60.0,
    "is_passed": true,
    "duration_used": 45,
    "correct_count": 42,
    "total_count": 50,
    "type_stats": {
      "single": {"correct": 18, "total": 20},
      "multi": {"correct": 8, "total": 10},
      "judge": {"correct": 10, "total": 10},
      "fill": {"correct": 4, "total": 5},
      "essay": {"correct": null, "total": 5}
    },
    "details": [
      {
        "question_id": 1,
        "type": "single",
        "content": "Python 是什么类型的语言？",
        "user_answer": "B",
        "correct_answer": "B",
        "is_correct": true,
        "score": 2.0,
        "max_score": 2.0,
        "explanation": "Python 是解释型语言"
      }
    ]
  },
  "message": "success"
}
```

#### GET /api/reports/overview
响应：200
```json
{
  "code": 0,
  "data": {
    "total_exams_taken": 15,
    "average_score": 72.5,
    "highest_score": 98.0,
    "pass_rate": 0.8,
    "total_questions_answered": 750
  },
  "message": "success"
}
```

#### GET /api/reports/trend
查询参数：`?days=30`
响应：200
```json
{
  "code": 0,
  "data": {
    "items": [
      {"date": "2026-05-01", "score": 75.0, "exam_title": "测试1"},
      {"date": "2026-05-15", "score": 82.0, "exam_title": "测试2"}
    ]
  },
  "message": "success"
}
```

---

## 6. 前端页面设计

### 6.1 注册/登录页 `/auth`

**布局**：居中卡片，Tab 切换注册/登录

**注册表单字段**：
- 用户名（3-50 字符）
- 邮箱（email 格式）
- 密码（6-20 字符）
- 确认密码

**登录表单字段**：
- 用户名/邮箱
- 密码

**交互**：
- 表单实时验证
- 登录成功后跳转 `/dashboard`
- 错误提示 Toast

### 6.2 仪表盘 `/dashboard`

**布局**：顶部导航栏 + 内容区

**内容区组件**：
- 欢迎语（用户名）
- 统计卡片（考试次数、平均分、通过率）
- 最近考试列表（最近 5 次）
- 快捷操作按钮（上传试卷、创建考试）

**导航栏**：仪表盘 | 上传 | 题库 | 考试 | 报告 | 退出

### 6.3 上传页 `/upload`

**布局**：左右分栏

**左栏**：文件上传区
- 拖拽上传区域
- 点击选择文件按钮
- 支持格式提示：仅 .docx，最大 10MB
- 上传进度条

**右栏**：解析预览区
- 题型统计（饼图或卡片）
- 题目列表（可展开查看详情）
- "确认入库" 按钮
- "重新上传" 按钮

### 6.4 题库页 `/questions`

**布局**：顶部筛选 + 题目列表

**筛选栏**：
- 题型下拉（全部/单选/多选/判断/填空/简答）
- 搜索框

**题目列表**：
- 题号、题型标签、题目内容摘要、分值
- 点击展开详情（选项、答案、解析）
- 删除按钮

**分页**：底部页码

### 6.5 创建考试页 `/exams/new`

**布局**：上部表单 + 下部选题

**表单区**：
- 考试标题
- 描述
- 时长（分钟）
- 满分
- 及格分

**选题区**：
- 左侧：题库列表（可筛选、勾选）
- 右侧：已选题目（可拖拽排序、移除）
- 分值设置（每题可自定义分值）

**操作按钮**：保存草稿 | 发布考试

### 6.6 考试列表页 `/exams`

**布局**：卡片列表或表格

**考试卡片/行**：
- 标题
- 状态标签（草稿/开放/关闭）
- 题数 / 满分 / 时长
- 操作按钮（查看详情、开始考试、关闭）

**筛选**：按状态筛选

### 6.7 答题页 `/exams/:id/take`

**布局**：左主右侧栏

**主区域**：
- 题号标记：当前题高亮，已答绿色，未答灰色
- 题目内容
- 选项（单选：radio，多选：checkbox，判断：radio 对/错）
- 输入框（填空：文本输入，简答：多行文本）
- 上一题 / 下一题按钮

**侧栏**：
- 倒计时（醒目显示）
- 答题进度条
- 题号网格（点击跳转）
- 提交按钮

**交互**：
- 切题时自动保存
- 每 30 秒自动保存
- 倒计时 ≤ 5 分钟时红色警告
- 时间到自动提交
- 提交前确认弹窗

### 6.8 结果页 `/attempts/:id/result`

**布局**：顶部概览 + 下部逐题

**概览区**：
- 大号分数显示
- 通过/未通过标签
- 用时
- 正确率

**题型统计**：每种题型的正确数/总数

**逐题回顾**：
- 题目内容
- 用户答案 vs 正确答案
- 对错标记（绿色对号/红色叉号）
- 得分
- 解析（如果有）

### 6.9 统计页 `/reports`

**布局**：统计卡片 + 图表

**统计卡片**：考试次数、平均分、最高分、通过率

**图表**：
- 成绩趋势折线图（X 轴：日期，Y 轴：分数）
- 题型正确率柱状图

---

## 7. Word 试卷格式规范

### 7.1 支持的试卷格式

系统需要解析结构化的 Word 试卷。以下为推荐格式：

```
一、单选题（每题 2 分，共 20 分）

1. Python 是什么类型的语言？
A. 编译型
B. 解释型
C. 汇编型
D. 机器语言
答案：B

2. ...

二、多选题（每题 3 分，共 15 分）

1. 以下哪些是 Python 的数据类型？
A. int
B. float
C. char
D. str
答案：A,B,D

三、判断题（每题 1 分，共 10 分）

1. Python 是一门面向对象的语言。（  ）
答案：正确

四、填空题（每题 2 分，共 10 分）

1. Python 中定义函数使用的关键字是 ______。
答案：def

五、简答题（每题 5 分，共 25 分）

1. 简述 Python 的特点。
答案：Python 具有简洁易读的语法、丰富的标准库、跨平台等特点。
```

### 7.2 解析规则

| 题型 | 识别特征 | 答案格式 |
|------|----------|----------|
| 单选题 | 题号 + 选项 A-D + 答案：单个字母 | `答案：B` |
| 多选题 | 题号 + 选项 A-D + 答案：多个字母逗号分隔 | `答案：A,B,D` |
| 判断题 | 题号 + （  ）+ 答案：正确/错误 | `答案：正确` |
| 填空题 | 题号 + 含下划线/空格 + 答案：文本 | `答案：def` |
| 简答题 | 题号 + 无选项 + 答案：长文本 | `答案：...` |

### 7.3 容错机制
- 允许题号后带点或不带点（`1.` 或 `1`）
- 允许答案格式变体（`答案：` / `参考答案：` / `答：`）
- 允许选项使用小写字母（`a.` → 自动转为 `A`）
- 判断题答案变体（`正确` / `对` / `√` → `正确`；`错误` / `错` / `×` → `错误`）

---

## 8. 错误处理

### 8.1 全局错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| 0 | 200/201 | 成功 |
| 1001 | 400 | 请求参数错误 |
| 1002 | 401 | 未提供 Token |
| 1003 | 401 | Token 已过期 |
| 1004 | 401 | Token 无效 |
| 1005 | 422 | 数据验证失败 |
| 2001 | 400 | 文件格式不支持 |
| 2002 | 400 | 文件大小超限 |
| 2003 | 500 | 文件解析失败 |
| 3001 | 404 | 考试不存在 |
| 3002 | 400 | 考试已关闭 |
| 3003 | 400 | 已参加过该考试 |
| 4001 | 404 | 答题记录不存在 |
| 4002 | 400 | 答题已提交 |
| 4003 | 400 | 答题时间已到 |
| 5001 | 500 | 服务器内部错误 |

### 8.2 前端错误处理
- API 错误：统一拦截，显示 Toast 提示
- 网络错误：显示 "网络连接失败，请重试"
- 401：自动跳转登录页
- 500：显示 "服务器错误，请稍后重试"
- 表单错误：字段级错误提示

---

## 9. 部署要求

### 9.1 开发环境
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- 操作系统：Windows/macOS/Linux

### 9.2 环境变量

**后端 `.env`**：
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/exam_system
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
CORS_ORIGINS=http://localhost:3000
```

**前端 `.env.local`**：
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```
