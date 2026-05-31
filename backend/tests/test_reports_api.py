"""成绩报告 API 测试 — FR-REPORT 模块全覆盖"""

from datetime import datetime, timedelta
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.main import app
from app.config import settings
from app.models.user import User
from app.models.exam import Exam, Question
from app.models.attempt import ExamAttempt, QuestionResponse
from app.utils.security import get_password_hash


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def setup_graded_attempt(db: Session, username: str = "report_user"):
    """创建一个已完成评分的考试作答记录，返回 (user, exam, questions, attempt)"""
    user = User(
        username=username,
        email=f"{username}@example.com",
        password_hash=get_password_hash("Test123456"),
    )
    db.add(user)
    db.flush()

    exam = Exam(
        title="报告测试考试",
        duration_minutes=60,
        total_score=100,
        pass_score=60,
        status="open",
        created_by=user.id,
    )
    db.add(exam)
    db.flush()

    questions = [
        Question(exam_id=exam.id, type="single", content="单选题1", answer="A", score=20, sort_order=1),
        Question(exam_id=exam.id, type="multi", content="多选题1", answer="A,B", score=20, sort_order=2),
        Question(exam_id=exam.id, type="judge", content="判断题1", answer="正确", score=20, sort_order=3),
        Question(exam_id=exam.id, type="fill", content="填空题1", answer="Python", score=20, sort_order=4),
        Question(exam_id=exam.id, type="essay", content="简答题1", answer="参考答案", score=20, sort_order=5),
    ]
    for q in questions:
        db.add(q)
    db.flush()

    attempt = ExamAttempt(
        exam_id=exam.id,
        user_id=user.id,
        status="graded",
        total_score=80,
        objective_score=80,
        subjective_score=None,
        submitted_at=datetime.now() - timedelta(days=1),
    )
    db.add(attempt)
    db.flush()

    responses = [
        QuestionResponse(attempt_id=attempt.id, question_id=questions[0].id, user_answer="A", is_correct=True, score=20, graded_by="auto"),
        QuestionResponse(attempt_id=attempt.id, question_id=questions[1].id, user_answer="A,B", is_correct=True, score=20, graded_by="auto"),
        QuestionResponse(attempt_id=attempt.id, question_id=questions[2].id, user_answer="正确", is_correct=True, score=20, graded_by="auto"),
        QuestionResponse(attempt_id=attempt.id, question_id=questions[3].id, user_answer="Java", is_correct=False, score=0, graded_by="auto"),
        QuestionResponse(attempt_id=attempt.id, question_id=questions[4].id, user_answer="我的答案", is_correct=None, score=None, graded_by="pending"),
    ]
    for r in responses:
        db.add(r)
    db.commit()

    return user, exam, questions, attempt


class TestAttemptResult:
    """TC-REPORT-01 ~ 06: 考试结果详情"""

    @pytest.mark.asyncio
    async def test_result_basic_info(self, client: AsyncClient):
        """TC-REPORT-01: 成绩详情 — 基本信息"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user, exam, questions, attempt = setup_graded_attempt(db, "result_basic")
            attempt_id = attempt.id

        login = await client.post("/api/auth/login", json={"username": "result_basic", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}/result",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["exam_title"] == "报告测试考试"
        assert data["total_score"] == 80
        assert data["pass_score"] == 60
        assert data["is_passed"] is True
        assert data["correct_count"] == 3
        assert data["total_questions"] == 5

    @pytest.mark.asyncio
    async def test_result_type_stats(self, client: AsyncClient):
        """TC-REPORT-02: 成绩详情 — 各题型统计"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user, exam, questions, attempt = setup_graded_attempt(db, "result_type")
            attempt_id = attempt.id

        login = await client.post("/api/auth/login", json={"username": "result_type", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}/result",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()["data"]
        type_stats = {s["type"]: s for s in data["type_stats"]}
        assert type_stats["single"]["correct"] == 1
        assert type_stats["single"]["total"] == 1
        assert type_stats["multi"]["correct"] == 1
        assert type_stats["judge"]["correct"] == 1
        assert type_stats["fill"]["correct"] == 0
        assert type_stats["essay"]["pending"] == 1

    @pytest.mark.asyncio
    async def test_result_correct_question(self, client: AsyncClient):
        """TC-REPORT-03: 逐题回顾 — 正确题目标记"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user, exam, questions, attempt = setup_graded_attempt(db, "result_correct")
            attempt_id = attempt.id

        login = await client.post("/api/auth/login", json={"username": "result_correct", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}/result",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()["data"]
        single_q = next(q for q in data["questions"] if q["type"] == "single")
        assert single_q["user_answer"] == "A"
        assert single_q["correct_answer"] == "A"
        assert single_q["is_correct"] is True
        assert single_q["earned_score"] == 20

    @pytest.mark.asyncio
    async def test_result_wrong_question(self, client: AsyncClient):
        """TC-REPORT-04: 逐题回顾 — 错误题目标记"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user, exam, questions, attempt = setup_graded_attempt(db, "result_wrong")
            attempt_id = attempt.id

        login = await client.post("/api/auth/login", json={"username": "result_wrong", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}/result",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()["data"]
        fill_q = next(q for q in data["questions"] if q["type"] == "fill")
        assert fill_q["user_answer"] == "Java"
        assert fill_q["correct_answer"] == "Python"
        assert fill_q["is_correct"] is False
        assert fill_q["earned_score"] == 0

    @pytest.mark.asyncio
    async def test_result_explanation(self, client: AsyncClient):
        """TC-REPORT-05: 逐题回顾 — 显示解析"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user = User(username="result_exp", email="result_exp@example.com", password_hash=get_password_hash("Test123456"))
            db.add(user)
            db.flush()
            exam = Exam(title="解析测试", duration_minutes=60, total_score=10, pass_score=6, status="open", created_by=user.id)
            db.add(exam)
            db.flush()
            q = Question(exam_id=exam.id, type="single", content="题1", answer="A", score=10, explanation="这是解析内容", sort_order=1)
            db.add(q)
            db.flush()
            attempt = ExamAttempt(exam_id=exam.id, user_id=user.id, status="graded", total_score=10, objective_score=10)
            db.add(attempt)
            db.flush()
            r = QuestionResponse(attempt_id=attempt.id, question_id=q.id, user_answer="A", is_correct=True, score=10, graded_by="auto")
            db.add(r)
            db.commit()
            attempt_id = attempt.id

        login = await client.post("/api/auth/login", json={"username": "result_exp", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}/result",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()["data"]
        assert data["questions"][0]["explanation"] == "这是解析内容"

    @pytest.mark.asyncio
    async def test_result_fail判定(self, client: AsyncClient):
        """TC-REPORT-06: 未通过判定"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user = User(username="result_fail", email="result_fail@example.com", password_hash=get_password_hash("Test123456"))
            db.add(user)
            db.flush()
            exam = Exam(title="不及格考试", duration_minutes=60, total_score=100, pass_score=60, status="open", created_by=user.id)
            db.add(exam)
            db.flush()
            q = Question(exam_id=exam.id, type="single", content="题1", answer="A", score=100, sort_order=1)
            db.add(q)
            db.flush()
            attempt = ExamAttempt(exam_id=exam.id, user_id=user.id, status="graded", total_score=30, objective_score=30)
            db.add(attempt)
            db.flush()
            r = QuestionResponse(attempt_id=attempt.id, question_id=q.id, user_answer="B", is_correct=False, score=0, graded_by="auto")
            db.add(r)
            db.commit()
            attempt_id = attempt.id

        login = await client.post("/api/auth/login", json={"username": "result_fail", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}/result",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()["data"]
        assert data["is_passed"] is False
        assert data["total_score"] == 30


class TestReportOverview:
    """TC-REPORT-07 ~ 08: 统计概览"""

    @pytest.mark.asyncio
    async def test_overview_with_data(self, client: AsyncClient):
        """TC-REPORT-07: 统计概览 — 有考试记录"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user, exam, questions, attempt = setup_graded_attempt(db, "overview_user")
            attempt2 = ExamAttempt(
                exam_id=exam.id,
                user_id=user.id,
                status="graded",
                total_score=40,
                objective_score=40,
            )
            db.add(attempt2)
            db.commit()

        login = await client.post("/api/auth/login", json={"username": "overview_user", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            "/api/reports/overview",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total_attempts"] == 2
        assert data["average_score"] == 60.0
        assert data["max_score"] == 80
        assert data["pass_rate"] == 50.0

    @pytest.mark.asyncio
    async def test_overview_empty(self, client: AsyncClient):
        """TC-REPORT-08: 统计概览 — 无考试记录"""
        await client.post("/api/auth/register", json={
            "username": "overview_empty",
            "email": "overview_empty@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "overview_empty", "password": "123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            "/api/reports/overview",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total_attempts"] == 0
        assert data["average_score"] == 0
        assert data["max_score"] == 0
        assert data["pass_rate"] == 0


class TestReportTrend:
    """TC-REPORT-09 ~ 10: 成绩趋势"""

    @pytest.mark.asyncio
    async def test_trend_with_data(self, client: AsyncClient):
        """TC-REPORT-09: 成绩趋势 — 有数据"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user, exam, questions, attempt = setup_graded_attempt(db, "trend_user")

        login = await client.post("/api/auth/login", json={"username": "trend_user", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            "/api/reports/trend?days=30",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1
        assert "date" in data[0]
        assert "score" in data[0]
        assert data[0]["score"] == 80

    @pytest.mark.asyncio
    async def test_trend_empty(self, client: AsyncClient):
        """TC-REPORT-10: 成绩趋势 — 无数据"""
        await client.post("/api/auth/register", json={
            "username": "trend_empty",
            "email": "trend_empty@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "trend_empty", "password": "123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            "/api/reports/trend?days=30",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 0
