"""安全与权限测试 — NFR-SEC 模块"""

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


class TestAnswerLeakage:
    """TC-SEC-08: 答案泄露防护"""

    @pytest.mark.asyncio
    async def test_start_exam_no_answer_leaked(self, client: AsyncClient):
        """开始考试时不返回正确答案"""
        await client.post("/api/auth/register", json={
            "username": "sec_user1",
            "email": "sec1@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "sec_user1", "password": "123456"})
        token = login.json()["data"]["access_token"]

        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user = db.query(User).filter(User.username == "sec_user1").first()
            exam = Exam(
                title="安全测试考试",
                duration_minutes=60,
                total_score=100,
                pass_score=60,
                status="open",
                created_by=user.id,
            )
            db.add(exam)
            db.flush()

            q = Question(
                exam_id=exam.id,
                type="single",
                content="答案泄露测试题",
                answer="B",
                score=10,
                explanation="这不应该被泄露",
                sort_order=1,
            )
            db.add(q)
            db.commit()
            exam_id = exam.id

        resp = await client.post(
            "/api/attempts",
            json={"exam_id": exam_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        questions = resp.json()["data"]["questions"]
        for q in questions:
            assert "answer" not in q, "不应返回正确答案"
            assert "explanation" not in q, "不应返回解析"

    @pytest.mark.asyncio
    async def test_attempt_progress_no_answer_leaked(self, client: AsyncClient):
        """获取答题进度时不返回正确答案"""
        await client.post("/api/auth/register", json={
            "username": "sec_user2",
            "email": "sec2@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "sec_user2", "password": "123456"})
        token = login.json()["data"]["access_token"]

        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            user = db.query(User).filter(User.username == "sec_user2").first()
            exam = Exam(title="安全考试2", duration_minutes=60, total_score=10, pass_score=6, status="open", created_by=user.id)
            db.add(exam)
            db.flush()
            q = Question(exam_id=exam.id, type="single", content="测试", answer="A", score=10, sort_order=1)
            db.add(q)
            db.commit()
            exam_id = exam.id

        start = await client.post(
            "/api/attempts",
            json={"exam_id": exam_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        attempt_id = start.json()["data"]["id"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        for q in resp.json()["data"]["questions"]:
            assert "answer" not in q, "进度查询不应返回答案"


class TestPermissionIsolation:
    """权限隔离 — 用户只能访问自己的数据"""

    @pytest.mark.asyncio
    async def test_cannot_access_other_user_attempt(self, client: AsyncClient):
        """不能访问他人的作答记录"""
        await client.post("/api/auth/register", json={
            "username": "perm_userA",
            "email": "permA@example.com",
            "password": "123456",
        })
        loginA = await client.post("/api/auth/login", json={"username": "perm_userA", "password": "123456"})
        tokenA = loginA.json()["data"]["access_token"]

        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            userA = db.query(User).filter(User.username == "perm_userA").first()
            exam = Exam(title="权限考试", duration_minutes=60, total_score=10, pass_score=6, status="open", created_by=userA.id)
            db.add(exam)
            db.flush()
            q = Question(exam_id=exam.id, type="single", content="测试", answer="A", score=10, sort_order=1)
            db.add(q)
            db.commit()
            exam_id = exam.id

        startA = await client.post(
            "/api/attempts",
            json={"exam_id": exam_id},
            headers={"Authorization": f"Bearer {tokenA}"},
        )
        attempt_id = startA.json()["data"]["id"]

        await client.post("/api/auth/register", json={
            "username": "perm_userB",
            "email": "permB@example.com",
            "password": "123456",
        })
        loginB = await client.post("/api/auth/login", json={"username": "perm_userB", "password": "123456"})
        tokenB = loginB.json()["data"]["access_token"]

        resp = await client.get(
            f"/api/attempts/{attempt_id}",
            headers={"Authorization": f"Bearer {tokenB}"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_cannot_submit_other_user_exam(self, client: AsyncClient):
        """不能提交他人的考试"""
        await client.post("/api/auth/register", json={
            "username": "submit_userA",
            "email": "submitA@example.com",
            "password": "123456",
        })
        loginA = await client.post("/api/auth/login", json={"username": "submit_userA", "password": "123456"})
        tokenA = loginA.json()["data"]["access_token"]

        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            userA = db.query(User).filter(User.username == "submit_userA").first()
            exam = Exam(title="提交权限考试", duration_minutes=60, total_score=10, pass_score=6, status="open", created_by=userA.id)
            db.add(exam)
            db.flush()
            q = Question(exam_id=exam.id, type="single", content="测试", answer="A", score=10, sort_order=1)
            db.add(q)
            db.commit()
            exam_id = exam.id

        startA = await client.post(
            "/api/attempts",
            json={"exam_id": exam_id},
            headers={"Authorization": f"Bearer {tokenA}"},
        )
        attempt_id = startA.json()["data"]["id"]

        await client.post("/api/auth/register", json={
            "username": "submit_userB",
            "email": "submitB@example.com",
            "password": "123456",
        })
        loginB = await client.post("/api/auth/login", json={"username": "submit_userB", "password": "123456"})
        tokenB = loginB.json()["data"]["access_token"]

        resp = await client.post(
            f"/api/attempts/{attempt_id}/submit",
            headers={"Authorization": f"Bearer {tokenB}"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_cannot_save_answers_other_user(self, client: AsyncClient):
        """不能修改他人的答案"""
        await client.post("/api/auth/register", json={
            "username": "save_userA",
            "email": "saveA@example.com",
            "password": "123456",
        })
        loginA = await client.post("/api/auth/login", json={"username": "save_userA", "password": "123456"})
        tokenA = loginA.json()["data"]["access_token"]

        db_engine = create_engine(settings.DATABASE_URL)
        with Session(db_engine) as db:
            userA = db.query(User).filter(User.username == "save_userA").first()
            exam = Exam(title="保存权限考试", duration_minutes=60, total_score=10, pass_score=6, status="open", created_by=userA.id)
            db.add(exam)
            db.flush()
            q = Question(exam_id=exam.id, type="single", content="测试", answer="A", score=10, sort_order=1)
            db.add(q)
            db.commit()
            exam_id = exam.id
            question_id = q.id

        startA = await client.post(
            "/api/attempts",
            json={"exam_id": exam_id},
            headers={"Authorization": f"Bearer {tokenA}"},
        )
        attempt_id = startA.json()["data"]["id"]

        await client.post("/api/auth/register", json={
            "username": "save_userB",
            "email": "saveB@example.com",
            "password": "123456",
        })
        loginB = await client.post("/api/auth/login", json={"username": "save_userB", "password": "123456"})
        tokenB = loginB.json()["data"]["access_token"]

        resp = await client.put(
            f"/api/attempts/{attempt_id}/answers",
            json={"answers": [{"question_id": question_id, "user_answer": "B"}]},
            headers={"Authorization": f"Bearer {tokenB}"},
        )
        assert resp.status_code == 403


class TestLoginWithEmail:
    """TC-AUTH-07: 邮箱登录"""

    @pytest.mark.asyncio
    async def test_login_with_email(self, client: AsyncClient):
        """使用邮箱登录"""
        await client.post("/api/auth/register", json={
            "username": "email_login",
            "email": "email_login@example.com",
            "password": "123456",
        })
        resp = await client.post("/api/auth/login", json={
            "username": "email_login@example.com",
            "password": "123456",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"


class TestInvalidTokens:
    """Token 无效场景"""

    @pytest.mark.asyncio
    async def test_malformed_token(self, client: AsyncClient):
        """篡改格式的 token"""
        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_token(self, client: AsyncClient):
        """空 token"""
        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer "},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_auth_scheme(self, client: AsyncClient):
        """错误的认证方案 (Basic 而非 Bearer)"""
        await client.post("/api/auth/register", json={
            "username": "scheme_user",
            "email": "scheme@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "scheme_user", "password": "123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Basic {token}"},
        )
        assert resp.status_code == 401
