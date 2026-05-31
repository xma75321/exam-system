"""
考试系统完整流程测试
测试所有 API 接口并生成测试报告
"""

import sys
import json
from datetime import datetime

sys.path.insert(0, "backend")

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from sqlalchemy import text

client = TestClient(app)

# 测试结果记录
test_results = []
current_flow = ""

def log_test(name, status, detail=""):
    """记录测试结果"""
    test_results.append({
        "flow": current_flow,
        "name": name,
        "status": "PASS" if status else "FAIL",
        "detail": detail
    })
    print(f"  [{'PASS' if status else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))

def cleanup():
    """清理测试数据"""
    with SessionLocal() as db:
        tables = [
            "options", "question_responses", "exam_attempts",
            "exams", "questions", "users"
        ]
        for table in tables:
            try:
                db.execute(text(f"DELETE FROM {table}"))
            except:
                pass
        db.commit()

print("=" * 60)
print("考试系统完整流程测试")
print("=" * 60)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 清理数据
print("[准备] 清理测试数据...")
cleanup()

# ============================================
# 流程1: 用户认证
# ============================================
current_flow = "用户认证"
print(f"\n{'='*60}")
print(f"流程1: {current_flow}")
print(f"{'='*60}")

# 1.1 注册
print("\n[1.1] 用户注册")
r = client.post("/api/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123456"
})
log_test("注册新用户", r.status_code == 201, f"状态码: {r.status_code}")

# 1.2 重复注册
print("\n[1.2] 重复注册")
r = client.post("/api/auth/register", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123456"
})
log_test("重复注册被拒绝", r.status_code == 400, f"状态码: {r.status_code}")

# 1.3 登录
print("\n[1.3] 用户登录")
r = client.post("/api/auth/login", json={
    "username": "testuser",
    "password": "Test123456"
})
login_success = r.status_code == 200 and "access_token" in r.json().get("data", {})
log_test("用户登录", login_success, f"状态码: {r.status_code}")
if login_success:
    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

# 1.4 错误密码登录
print("\n[1.4] 错误密码登录")
r = client.post("/api/auth/login", json={
    "username": "testuser",
    "password": "WrongPassword"
})
log_test("错误密码被拒绝", r.status_code == 401, f"状态码: {r.status_code}")

# 1.5 获取用户信息
print("\n[1.5] 获取用户信息")
r = client.get("/api/auth/me", headers=headers)
me_success = r.status_code == 200 and r.json()["data"]["username"] == "testuser"
log_test("获取用户信息", me_success, f"状态码: {r.status_code}")

# ============================================
# 流程2: 试卷上传
# ============================================
current_flow = "试卷上传"
print(f"\n{'='*60}")
print(f"流程2: {current_flow}")
print(f"{'='*60}")

# 2.1 上传试卷（模拟）
print("\n[2.1] 上传试卷文件")
# 由于需要真实文件，我们直接测试解析后的保存接口
test_questions = [
    {
        "type": "single",
        "content": "Python中哪个关键字用于定义函数？",
        "score": 10,
        "options": [
            {"label": "A", "content": "def", "is_correct": True},
            {"label": "B", "content": "function", "is_correct": False},
            {"label": "C", "content": "func", "is_correct": False},
            {"label": "D", "content": "define", "is_correct": False}
        ],
        "answer": "A"
    },
    {
        "type": "judge",
        "content": "Python是一种编译型语言。",
        "score": 10,
        "answer": "false"
    },
    {
        "type": "fill",
        "content": "Python中用于输出的函数是____。",
        "score": 10,
        "answer": "print"
    },
    {
        "type": "essay",
        "content": "请简述Python的特点。",
        "score": 20,
        "answer": ""
    }
]

# 2.2 保存题目
print("\n[2.2] 保存题目到数据库")
r = client.post("/api/upload/confirm", 
    headers=headers,
    json={
        "filename": "test_paper.docx",
        "questions": test_questions
    }
)
save_success = r.status_code in [200, 201]
log_test("保存题目", save_success, f"状态码: {r.status_code}")
if save_success:
    saved_data = r.json()["data"]
    print(f"    保存了 {len(saved_data['questions'])} 道题目")

# ============================================
# 流程3: 题库管理
# ============================================
current_flow = "题库管理"
print(f"\n{'='*60}")
print(f"流程3: {current_flow}")
print(f"{'='*60}")

# 3.1 获取题目列表
print("\n[3.1] 获取题目列表")
r = client.get("/api/questions?page=1&page_size=10", headers=headers)
list_success = r.status_code == 200 and r.json()["data"]["total"] > 0
log_test("获取题目列表", list_success, f"总数: {r.json()['data']['total']}")

# 3.2 按题型筛选
print("\n[3.2] 按题型筛选")
r = client.get("/api/questions?page=1&page_size=10&type=single", headers=headers)
filter_success = r.status_code == 200
log_test("按题型筛选", filter_success, f"单选题数量: {r.json()['data']['total']}")

# 3.3 获取题目详情
print("\n[3.3] 获取题目详情")
# 先获取一道题的ID
r = client.get("/api/questions?page=1&page_size=1", headers=headers)
if r.json()["data"]["items"]:
    q_id = r.json()["data"]["items"][0]["id"]
    r = client.get(f"/api/questions/{q_id}", headers=headers)
    detail_success = r.status_code == 200
    log_test("获取题目详情", detail_success, f"题目ID: {q_id}")

# ============================================
# 流程4: 考试管理
# ============================================
current_flow = "考试管理"
print(f"\n{'='*60}")
print(f"流程4: {current_flow}")
print(f"{'='*60}")

# 4.1 获取题目ID列表
print("\n[4.1] 获取题目ID列表")
r = client.get("/api/questions?page=1&page_size=10", headers=headers)
question_ids = [q["id"] for q in r.json()["data"]["items"]]
print(f"    可用题目: {question_ids}")

# 4.2 创建考试
print("\n[4.2] 创建考试")
r = client.post("/api/exams",
    headers=headers,
    json={
        "title": "Python基础测试",
        "description": "测试Python基础知识",
        "duration_minutes": 60,
        "total_score": 50,
        "pass_score": 30,
        "question_ids": question_ids[:4]
    }
)
create_success = r.status_code in [200, 201]
log_test("创建考试", create_success, f"状态码: {r.status_code}")
if create_success:
    exam_id = r.json()["data"]["id"]
    print(f"    考试ID: {exam_id}")

# 4.3 获取考试列表
print("\n[4.3] 获取考试列表")
r = client.get("/api/exams?page=1&page_size=10", headers=headers)
list_success = r.status_code == 200 and r.json()["data"]["total"] > 0
log_test("获取考试列表", list_success, f"总数: {r.json()['data']['total']}")

# 4.4 发布考试
print("\n[4.4] 发布考试")
r = client.post(f"/api/exams/{exam_id}/publish", headers=headers)
publish_success = r.status_code == 200 and r.json()["data"]["status"] == "open"
log_test("发布考试", publish_success, f"状态: {r.json()['data']['status']}")

# 4.5 关闭考试
print("\n[4.5] 关闭考试")
r = client.post(f"/api/exams/{exam_id}/close", headers=headers)
close_success = r.status_code == 200 and r.json()["data"]["status"] == "closed"
log_test("关闭考试", close_success, f"状态: {r.json()['data']['status']}")

# 4.6 重新发布（用于后续测试）
print("\n[4.6] 重新发布考试")
r = client.post(f"/api/exams/{exam_id}/publish", headers=headers)

# ============================================
# 流程5: 考试答题
# ============================================
current_flow = "考试答题"
print(f"\n{'='*60}")
print(f"流程5: {current_flow}")
print(f"{'='*60}")

# 5.1 开始考试
print("\n[5.1] 开始考试")
r = client.post("/api/attempts",
    headers=headers,
    json={"exam_id": exam_id}
)
start_success = r.status_code in [200, 201]
log_test("开始考试", start_success, f"状态码: {r.status_code}")
if start_success:
    attempt_id = r.json()["data"]["id"]
    attempt_questions = r.json()["data"]["questions"]
    print(f"    答题ID: {attempt_id}")
    print(f"    题目数量: {len(attempt_questions)}")

# 5.2 保存答案
print("\n[5.2] 保存答案")
answers = []
for q in attempt_questions:
    if q["type"] == "single":
        answers.append({"question_id": q["id"], "user_answer": "A"})
    elif q["type"] == "multi":
        answers.append({"question_id": q["id"], "user_answer": "A,B"})
    elif q["type"] == "judge":
        answers.append({"question_id": q["id"], "user_answer": "false"})
    elif q["type"] == "fill":
        answers.append({"question_id": q["id"], "user_answer": "print"})
    elif q["type"] == "essay":
        answers.append({"question_id": q["id"], "user_answer": "Python是一种解释型、面向对象的编程语言"})

r = client.put(f"/api/attempts/{attempt_id}/answers",
    headers=headers,
    json={"answers": answers}
)
save_success = r.status_code == 200
log_test("保存答案", save_success, f"状态码: {r.status_code}")

# 5.3 获取答题进度
print("\n[5.3] 获取答题进度")
r = client.get(f"/api/attempts/{attempt_id}", headers=headers)
progress_success = r.status_code == 200 and len(r.json()["data"]["answered"]) > 0
log_test("获取答题进度", progress_success, f"已答: {len(r.json()['data']['answered'])} 题")

# 5.4 提交考试
print("\n[5.4] 提交考试")
r = client.post(f"/api/attempts/{attempt_id}/submit", headers=headers)
submit_success = r.status_code == 200
log_test("提交考试", submit_success, f"状态码: {r.status_code}")

# ============================================
# 流程6: 评分
# ============================================
current_flow = "评分"
print(f"\n{'='*60}")
print(f"流程6: {current_flow}")
print(f"{'='*60}")

# 6.1 获取考试结果
print("\n[6.1] 获取考试结果")
r = client.get(f"/api/attempts/{attempt_id}/result", headers=headers)
result_success = r.status_code == 200
log_test("获取考试结果", result_success, f"状态码: {r.status_code}")
if result_success:
    result_data = r.json()["data"]
    print(f"    客观题得分: {result_data.get('objective_score', 'N/A')}")
    print(f"    总分: {result_data.get('total_score', 'N/A')}")
    print(f"    是否通过: {result_data.get('is_passed', 'N/A')}")

# ============================================
# 流程7: 统计报表
# ============================================
current_flow = "统计报表"
print(f"\n{'='*60}")
print(f"流程7: {current_flow}")
print(f"{'='*60}")

# 7.1 获取统计总览
print("\n[7.1] 获取统计总览")
r = client.get("/api/reports/overview", headers=headers)
overview_success = r.status_code == 200
log_test("获取统计总览", overview_success, f"状态码: {r.status_code}")
if overview_success:
    overview = r.json()["data"]
    print(f"    考试次数: {overview.get('total_attempts', 0)}")
    print(f"    平均分: {overview.get('average_score', 0)}")
    print(f"    通过率: {overview.get('pass_rate', 0)}%")

# 7.2 获取成绩趋势
print("\n[7.2] 获取成绩趋势")
r = client.get("/api/reports/trend?days=30", headers=headers)
trend_success = r.status_code == 200
log_test("获取成绩趋势", trend_success, f"数据条数: {len(r.json()['data'])}")

# ============================================
# 清理测试数据
# ============================================
print(f"\n{'='*60}")
print("清理测试数据")
print(f"{'='*60}")
cleanup()
print("[OK] 测试数据已清理")

# ============================================
# 生成测试报告
# ============================================
print(f"\n{'='*60}")
print("测试报告")
print(f"{'='*60}")

# 统计结果
total = len(test_results)
passed = len([r for r in test_results if "PASS" in r["status"]])
failed = len([r for r in test_results if "FAIL" in r["status"]])

print(f"\n总计: {total} 项测试")
print(f"通过: {passed} 项")
print(f"失败: {failed} 项")
print(f"通过率: {passed/total*100:.1f}%")

# 按流程分组显示
print("\n" + "-" * 60)
for flow in dict.fromkeys([r["flow"] for r in test_results]):
    print(f"\n【{flow}】")
    for r in test_results:
        if r["flow"] == flow:
            print(f"  {r['status']} {r['name']}" + (f" ({r['detail']})" if r["detail"] else ""))

# 保存测试报告到文件
report = {
    "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "total": total,
    "passed": passed,
    "failed": failed,
    "pass_rate": f"{passed/total*100:.1f}%",
    "results": test_results
}

with open("test_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n测试报告已保存到: test_report.json")
print("=" * 60)
