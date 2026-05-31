"""答题进度查询测试 — GET /api/attempts/:id"""

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


@pytest.fixture
async def attempt_setup(client: AsyncClient):
    """注册用户、创建考试、开始考试，返回 token 和 attempt_id"""
    await client.post("/api/auth/register", json={
        "username": "progress_user",
        "email": "progress@example.com",
        "password": "123456",
    })
    login = await client.post("/api/auth/login", json={"username": "progress_user", "password": "123456"})
    token = login.json()["data"]["access_token"]

    db_engine = create_engine(settings.DATABASE_URL)
    with Session(db_engine) as db:
        user = db.query(User).filter(User.username == "progress_user").first()
        exam = Exam(title="进度测试", duration_minutes=60, total_score=100, pass_score=60, status="open", created_by=user.id)
        db.add(exam)
        db.flush()
        q1 = Question(exam_id=exam.id, type="single", content="题1", answer="A", score=50, sort_order=1)
        q2 = Question(exam_id=exam.id, type="judge", content="题2", answer="正确", score=50, sort_order=2)
        db.add(q1)
        db.add(q2)
        db.commit()
        exam_id = exam.id

    start = await client.post(
        "/api/attempts",
        json={"exam_id": exam_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    attempt_id = start.json()["data"]["id"]
    return token, attempt_id


class TestAttemptProgress:
    """TC-TAKE-05: 获取答题进度"""

    @pytest.mark.asyncio
    async def test_get_progress(self, client: AsyncClient, attempt_setup):
        """获取答题进度"""
        token, attempt_id = attempt_setup

        resp = await client.get(
            f"/api/attempts/{attempt_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["status"] == "in_progress"
        assert data["exam_title"] == "进度测试"
        assert len(data["questions"]) == 2
        assert len(data["answered"]) == 0  # 还没答题

    @pytest.mark.asyncio
    async def test_progress_shows_saved_answers(self, client: AsyncClient, attempt_setup):
        """保存答案后进度中可见"""
        token, attempt_id = attempt_setup

        # 获取 question_id
        resp = await client.get(
            f"/api/attempts/{attempt_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        question_id = resp.json()["data"]["questions"][0]["id"]

        # 保存答案
        await client.put(
            f"/api/attempts/{attempt_id}/answers",
            json={"answers": [{"question_id": question_id, "user_answer": "A"}]},
            headers={"Authorization": f"Bearer {token}"},
        )

        # 再次获取进度
        resp = await client.get(
            f"/api/attempts/{attempt_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()["data"]
        assert len(data["answered"]) == 1
        assert data["answered"][0]["user_answer"] == "A"

    @pytest.mark.asyncio
    async def test_progress_not_found(self, client: AsyncClient):
        """不存在的 attempt 返回 404"""
        await client.post("/api/auth/register", json={
            "username": "progress_404",
            "email": "progress404@example.com",
            "password": "123456",
        })
        login = await client.post("/api/auth/login", json={"username": "progress_404", "password": "123456"})
        token = login.json()["data"]["access_token"]

        resp = await client.get(
            "/api/attempts/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404
