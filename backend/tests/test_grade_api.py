"""评分 API 测试 — POST /api/attempts/:id/grade"""

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


def setup_ungraded_attempt(db: Session, username: str = "grade_api_user"):
    """创建一个已提交但未评分的作答记录"""
    user = User(
        username=username,
        email=f"{username}@example.com",
        password_hash=get_password_hash("Test123456"),
    )
    db.add(user)
    db.flush()

    exam = Exam(
        title="评分API测试",
        duration_minutes=60,
        total_score=100,
        pass_score=60,
        status="open",
        created_by=user.id,
    )
    db.add(exam)
    db.flush()

    questions = [
        Question(exam_id=exam.id, type="single", content="单选", answer="A", score=20, sort_order=1),
        Question(exam_id=exam.id, type="multi", content="多选", answer="A,B", score=30, sort_order=2),
        Question(exam_id=exam.id, type="judge", content="判断", answer="正确", score=20, sort_order=3),
        Question(exam_id=exam.id, type="fill", content="填空", answer="Python", score=15, sort_order=4),
        Question(exam_id=exam.id, type="essay", content="简答", answer="参考", score=15, sort_order=5),
    ]
    for q in questions:
        db.add(q)
    db.flush()

    attempt = ExamAttempt(
        exam_id=exam.id,
        user_id=user.id,
        status="submitted",
    )
    db.add(attempt)
    db.flush()

    responses = [
        QuestionResponse(attempt_id=attempt.id, question_id=questions[0].id, user_answer="A"),
        QuestionResponse(attempt_id=attempt.id, question_id=questions[1].id, user_answer="A,B"),
        QuestionResponse(attempt_id=attempt.id, question_id=questions[2].id, user_answer="正确"),
        QuestionResponse(attempt_id=attempt.id, question_id=questions[3].id, user_answer="Python"),
        QuestionResponse(attempt_id=attempt.id, question_id=questions[4].id, user_answer="我的答案"),
    ]
    for r in responses:
        db.add(r)
    db.commit()

    return user, exam, questions, attempt


class TestGradeAPI:
    """评分接口测试"""

    @pytest.mark.asyncio
    async def test_trigger_grade_success(self, client: AsyncClient):
        """手动触发评分成功"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user, exam, questions, attempt = setup_ungraded_attempt(db, "grade_trigger")
            attempt_id = attempt.id

        login = await client.post("/api/auth/login", json={"username": "grade_trigger", "password": "Test123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.post(
            f"/api/attempts/{attempt_id}/grade",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["status"] == "graded"
        assert data["total_score"] == 85.0  # 20+30+20+15+0(essay)
        assert data["objective_score"] == 85.0

    @pytest.mark.asyncio
    async def test_grade_not_found(self, client: AsyncClient):
        """对不存在的 attempt 评分"""
        await client.post("/api/auth/register", json={
            "username": "grade_notfound",
            "email": "grade_notfound@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "grade_notfound", "password": "123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.post(
            "/api/attempts/99999/grade",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_grade_permission_denied(self, client: AsyncClient):
        """不能给别人的 attempt 评分"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user, exam, questions, attempt = setup_ungraded_attempt(db, "grade_owner")
            attempt_id = attempt.id

        # 另一个用户尝试评分
        await client.post("/api/auth/register", json={
            "username": "grade_other",
            "email": "grade_other@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "grade_other", "password": "123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.post(
            f"/api/attempts/{attempt_id}/grade",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403


class TestAttemptResultAPI:
    """结果查看 API 测试"""

    @pytest.mark.asyncio
    async def test_result_not_submitted(self, client: AsyncClient):
        """未提交的考试不能查看结果"""
        await client.post("/api/auth/register", json={
            "username": "result_not_sub",
            "email": "result_not_sub@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "result_not_sub", "password": "123456"})
        token = login.json()["data"]["access_token"]

        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user = db.query(User).filter(User.username == "result_not_sub").first()
            exam = Exam(title="未提交考试", duration_minutes=60, total_score=10, pass_score=6, status="open", created_by=user.id)
            db.add(exam)
            db.flush()
            attempt = ExamAttempt(exam_id=exam.id, user_id=user.id, status="in_progress")
            db.add(attempt)
            db.commit()
            attempt_id = attempt.id

        resp = await client.get(
            f"/api/attempts/{attempt_id}/result",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_result_permission_denied(self, client: AsyncClient):
        """不能查看他人的结果"""
        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user = User(username="result_owner", email="result_owner@example.com", password_hash=get_password_hash("Test123456"))
            db.add(user)
            db.flush()
            exam = Exam(title="他人考试", duration_minutes=60, total_score=10, pass_score=6, status="open", created_by=user.id)
            db.add(exam)
            db.flush()
            attempt = ExamAttempt(exam_id=exam.id, user_id=user.id, status="graded", total_score=10, objective_score=10)
            db.add(attempt)
            db.commit()
            attempt_id = attempt.id

        await client.post("/api/auth/register", json={
            "username": "result_other",
            "email": "result_other@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "result_other", "password": "123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}/result",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
