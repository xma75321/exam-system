# 智能考试系统（MVP）— 测试执行报告

## 报告信息

| 项目 | 内容 |
|------|------|
| 测试日期 | 2026-05-30 |
| 测试范围 | 全功能模块 API 测试 + 安全测试 |
| 执行环境 | Python 3.13, FastAPI, MySQL 8, pytest + httpx |
| 测试用例总数 | 121 条 |
| 通过 | **117 条** |
| 预期失败（已确认缺陷） | **4 条** |
| **通过率** | **96.7%**（不含已知缺陷）/ **100%**（含 xfail） |

---

## 1. 测试执行结果汇总

### 1.1 各模块结果

| 模块 | 用例数 | 通过 | xfail | 状态 |
|------|--------|------|-------|------|
| 用户注册 FR-AUTH (register) | 6 | 6 | 0 | ✅ |
| 用户登录 FR-AUTH (login) | 7 | 7 | 0 | ✅ |
| 试卷上传 FR-PARSE (upload) | 4 | 4 | 0 | ✅ |
| Word 解析器 (parsers) | 25 | 25 | 0 | ✅ |
| 题目入库 FR-PARSE (confirm) | 4 | 4 | 0 | ✅ |
| 题库管理 FR-QB | 6 | 6 | 0 | ✅ |
| 考试管理 FR-EXAM (CRUD) | 10 | 10 | 0 | ✅ |
| 考试状态机 FR-EXAM (state) | 5 | 1 | **4** | ⚠️ 缺陷 |
| 答题模块 FR-TAKE | 9 | 9 | 0 | ✅ |
| 评分模块 FR-GRADE (service) | 15 | 15 | 0 | ✅ |
| 评分 API FR-GRADE (api) | 5 | 5 | 0 | ✅ |
| 手动评分 FR-GRADE (manual) | 4 | 4 | 0 | ✅ |
| 成绩报告 FR-REPORT | 10 | 10 | 0 | ✅ |
| 安全与权限 NFR-SEC | 9 | 9 | 0 | ✅ |
| **合计** | **121** | **117** | **4** | |

### 1.2 新增测试用例（本次执行补充）

在原有 89 条基础上，新增 32 条用例覆盖了以下此前缺失的测试点：

| 新增文件 | 用例数 | 覆盖内容 |
|----------|--------|----------|
| `test_reports_api.py` | 10 | FR-REPORT 全覆盖：成绩详情、题型统计、逐题回顾（对/错/解析）、通过/未通过判定、统计概览（有数据/空）、成绩趋势（有数据/空） |
| `test_exam_state.py` | 5 | 状态机完整性：正常流转 draft→open→closed、禁止 open→open、closed→open、draft→closed、closed→closed |
| `test_grade_api.py` | 5 | 评分 API：手动触发评分、attempt 不存在、权限隔离、未提交不能查看结果、他人结果不可查看 |
| `test_attempt_progress.py` | 3 | 答题进度：获取进度、保存答案后可见、不存在返回 404 |
| `test_security.py` | 9 | 安全：答题时不泄露答案、进度查询不泄露答案、权限隔离（3 场景）、邮箱登录、token 篡改/空/错误 scheme |

---

## 2. 发现的缺陷

### 🔴 BUG-01: 考试状态转换无校验（严重）

| 项目 | 内容 |
|------|------|
| **缺陷编号** | BUG-01 |
| **严重级别** | 高 |
| **影响范围** | `app/services/exam_service.py` — `publish_exam()` 和 `close_exam()` |
| **问题描述** | `publish_exam()` 不校验当前状态是否为 `draft`，任意状态（open/closed）均可被"发布"为 open。`close_exam()` 不校验当前状态是否为 `open`，任意状态（draft/closed）均可被"关闭"为 closed。 |
| **SPEC 要求** | 状态机应为 `draft → open → closed`，closed 不可逆 |
| **实际行为** | 状态可任意转换，违反业务约束 |
| **复现步骤** | 1. 创建考试（draft）2. POST `/exams/:id/close` → 返回 200，状态变为 closed（应为 400） |
| **修复建议** | 在 `publish_exam()` 中加入 `if exam.status != "draft": raise ValueError("仅草稿可发布")`；在 `close_exam()` 中加入 `if exam.status != "open": raise ValueError("仅开放中考试可关闭")` |

**关联用例：**
- `test_cannot_publish_open_exam` — xfail
- `test_cannot_publish_closed_exam` — xfail
- `test_cannot_close_draft_exam` — xfail
- `test_cannot_close_closed_exam` — xfail

---

## 3. 测试覆盖矩阵（TEST_PLAN → 实际执行）

| TEST_PLAN 编号 | 对应实际用例 | 状态 |
|----------------|-------------|------|
| TC-AUTH-01 ~ 06 | test_auth_register.py (6 条) | ✅ |
| TC-AUTH-07 | test_security.py::test_login_with_email | ✅ |
| TC-AUTH-08 ~ 09 | test_auth_login.py::test_login_wrong_password / nonexistent | ✅ |
| TC-AUTH-10 | test_auth_login.py::test_me_with_token | ✅ |
| TC-AUTH-11 | test_auth_login.py::test_me_without_token | ✅ |
| TC-AUTH-12 | test_auth_login.py::test_me_with_invalid_token + test_security.py (3 条) | ✅ |
| TC-PARSE-01 | test_upload.py::test_upload_docx_success | ✅ |
| TC-PARSE-02 | test_upload.py::test_upload_non_docx_file | ✅ |
| TC-PARSE-05 ~ 13 | test_choice/judge/fill/essay_parser.py (25 条) | ✅ |
| TC-PARSE-15 | test_question_save.py (4 条) | ✅ |
| TC-QB-01 ~ 07 | test_questions_api.py (6 条) | ✅ |
| TC-EXAM-01 ~ 12 | test_exams_api.py (10 条) | ✅ |
| TC-EXAM-13 | test_exam_state.py (5 条) | ⚠️ 1 pass + 4 xfail |
| TC-TAKE-01/03/04/06/07 | test_attempts_api.py (6 条) | ✅ |
| TC-TAKE-05 | test_attempt_progress.py (3 条) | ✅ |
| TC-GRADE-01 ~ 12 | test_grade_service.py (15 条) | ✅ |
| TC-GRADE-11 | test_manual_grade.py (4 条) | ✅ |
| TC-GRADE-06 (API) | test_grade_api.py (5 条) | ✅ |
| TC-REPORT-01 ~ 06 | test_reports_api.py::TestAttemptResult (6 条) | ✅ |
| TC-REPORT-07 ~ 08 | test_reports_api.py::TestReportOverview (2 条) | ✅ |
| TC-REPORT-09 ~ 10 | test_reports_api.py::TestReportTrend (2 条) | ✅ |
| TC-SEC-08 | test_security.py::TestAnswerLeakage (2 条) | ✅ |
| 权限隔离 | test_security.py::TestPermissionIsolation (3 条) | ✅ |

---

## 4. 未覆盖项（需前端 E2E 测试）

以下为 API 测试无法覆盖的场景，需要前端 E2E 测试（Playwright/Cypress）补充：

| TEST_PLAN 编号 | 原因 |
|----------------|------|
| TC-UI-AUTH-01 ~ 06 | 前端 UI 交互（Tab 切换、表单验证、Toast 提示） |
| TC-UI-DASH-01 ~ 04 | 导航栏、统计卡片渲染 |
| TC-UI-UP-01 ~ 04 | 拖拽上传、进度条 |
| TC-UI-QB-01 ~ 03 | 题目展开、筛选交互 |
| TC-UI-EXAM-01 ~ 03 | 选题区拖拽排序 |
| TC-UI-TAKE-01 ~ 05 | 答题页题型展示、计时器 UI、提交确认弹窗 |
| TC-UI-RES-01 ~ 03 | 结果页颜色标记、图表 |
| TC-UI-RPT-01 ~ 02 | 折线图渲染 |
| TC-PERF-01 ~ 04 | 性能指标（P95 < 500ms、并发 50 人等） |
| TC-REL-02 | 计时器防篡改（需前端+服务端联合测试） |
| TC-COMP-01 ~ 05 | 跨浏览器兼容性 |

---

## 5. 建议

1. **立即修复 BUG-01**（状态机校验缺失）— 这是一个业务逻辑缺陷，可能导致考试管理混乱
2. **补充 E2E 测试** — 当前仅覆盖 API 层，前端交互完全未测试，建议使用 Playwright 补充
3. **性能测试** — 建议使用 JMeter/k6 对 API 进行压力测试，验证 NFR-PERF 指标
4. **修复 DeprecationWarning** — `datetime.utcnow()` 在 Python 3.13 已弃用，建议迁移至 `datetime.now(datetime.UTC)`
