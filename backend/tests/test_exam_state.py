"""考试状态机测试 — 状态流转完整性"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def token_and_questions(client: AsyncClient):
    """注册用户、创建题目，返回 token 和 question_ids"""
    await client.post("/api/auth/register", json={
        "username": "state_user",
        "email": "state@test.com",
        "password": "123456",
    })
    login = await client.post("/api/auth/login", json={"username": "state_user", "password": "123456"})
    token = login.json()["data"]["access_token"]

    resp = await client.post(
        "/api/upload/confirm",
        json={
            "filename": "state_test.docx",
            "questions": [
                {
                    "temp_id": "q1", "type": "single",
                    "content": "状态测试题",
                    "options": [{"label": "A", "content": "选A"}, {"label": "B", "content": "选B"}],
                    "answer": "A", "score": 10,
                },
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    question_ids = [q["id"] for q in resp.json()["data"]["questions"]]
    return token, question_ids


async def create_exam(client, token, question_ids, title="状态测试考试"):
    """创建一个 draft 状态考试"""
    resp = await client.post(
        "/api/exams",
        json={
            "title": title,
            "description": "描述",
            "duration_minutes": 60,
            "total_score": 10,
            "pass_score": 6,
            "question_ids": question_ids,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["data"]["id"]


class TestStateMachine:
    """TC-EXAM-13: 状态机完整性"""

    @pytest.mark.asyncio
    async def test_full_state_flow(self, client: AsyncClient, token_and_questions):
        """正常流转: draft -> open -> closed"""
        token, question_ids = token_and_questions
        exam_id = await create_exam(client, token, question_ids)

        # draft -> open
        resp = await client.post(
            f"/api/exams/{exam_id}/publish",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "open"

        # open -> closed
        resp = await client.post(
            f"/api/exams/{exam_id}/close",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "closed"

    @pytest.mark.xfail(reason="BUG: publish_exam 不校验当前状态，允许非 draft 发布")
    @pytest.mark.asyncio
    async def test_cannot_publish_open_exam(self, client: AsyncClient, token_and_questions):
        """TC-EXAM-10: open 状态不能再次发布"""
        token, question_ids = token_and_questions
        exam_id = await create_exam(client, token, question_ids, title="重复发布测试")

        # 先发布
        await client.post(
            f"/api/exams/{exam_id}/publish",
            headers={"Authorization": f"Bearer {token}"},
        )

        # 再次发布应失败
        resp = await client.post(
            f"/api/exams/{exam_id}/publish",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.xfail(reason="BUG: publish_exam 不校验当前状态，允许 closed 状态发布")
    @pytest.mark.asyncio
    async def test_cannot_publish_closed_exam(self, client: AsyncClient, token_and_questions):
        """closed 状态不能再发布"""
        token, question_ids = token_and_questions
        exam_id = await create_exam(client, token, question_ids, title="关闭后发布测试")

        # draft -> open -> closed
        await client.post(f"/api/exams/{exam_id}/publish", headers={"Authorization": f"Bearer {token}"})
        await client.post(f"/api/exams/{exam_id}/close", headers={"Authorization": f"Bearer {token}"})

        # closed -> 发布应失败
        resp = await client.post(
            f"/api/exams/{exam_id}/publish",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.xfail(reason="BUG: close_exam 不校验当前状态，允许 draft 状态关闭")
    @pytest.mark.asyncio
    async def test_cannot_close_draft_exam(self, client: AsyncClient, token_and_questions):
        """TC-EXAM-12: draft 状态不能关闭"""
        token, question_ids = token_and_questions
        exam_id = await create_exam(client, token, question_ids, title="草稿关闭测试")

        resp = await client.post(
            f"/api/exams/{exam_id}/close",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.xfail(reason="BUG: close_exam 不校验当前状态，允许 closed 状态再次关闭")
    @pytest.mark.asyncio
    async def test_cannot_close_closed_exam(self, client: AsyncClient, token_and_questions):
        """closed 状态不能再关闭"""
        token, question_ids = token_and_questions
        exam_id = await create_exam(client, token, question_ids, title="重复关闭测试")

        await client.post(f"/api/exams/{exam_id}/publish", headers={"Authorization": f"Bearer {token}"})
        await client.post(f"/api/exams/{exam_id}/close", headers={"Authorization": f"Bearer {token}"})

        resp = await client.post(
            f"/api/exams/{exam_id}/close",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400
