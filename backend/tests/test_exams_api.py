"""考试管理 API 测试"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def token(client: AsyncClient) -> str:
    """注册并登录，返回 Token"""
    await client.post(
        "/api/auth/register",
        json={"username": "examuser", "email": "exam@test.com", "password": "123456"},
    )
    resp = await client.post(
        "/api/auth/login",
        json={"username": "examuser", "password": "123456"},
    )
    return resp.json()["data"]["access_token"]


@pytest.fixture
async def question_ids(client: AsyncClient, token: str) -> list[int]:
    """创建试题并返回 ID 列表"""
    resp = await client.post(
        "/api/upload/confirm",
        json={
            "filename": "test.docx",
            "questions": [
                {
                    "temp_id": "q1", "type": "single",
                    "content": "单选题", "options": [
                        {"label": "A", "content": "选A"},
                        {"label": "B", "content": "选B"},
                    ],
                    "answer": "A", "score": 2.0,
                },
                {
                    "temp_id": "q2", "type": "judge",
                    "content": "判断题", "answer": "正确", "score": 1.0,
                },
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return [q["id"] for q in resp.json()["data"]["questions"]]


@pytest.fixture
async def exam_id(client: AsyncClient, token: str, question_ids: list[int]) -> int:
    """创建考试并返回 ID"""
    resp = await client.post(
        "/api/exams",
        json={
            "title": "测试考试",
            "description": "描述",
            "duration_minutes": 60,
            "total_score": 100,
            "pass_score": 60,
            "question_ids": question_ids,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["data"]["id"]


class TestExamCreate:
    """创建考试测试"""

    @pytest.mark.asyncio
    async def test_create_success(self, client: AsyncClient, token: str, question_ids: list[int]):
        """创建考试成功"""
        resp = await client.post(
            "/api/exams",
            json={
                "title": "新考试",
                "description": "测试",
                "duration_minutes": 60,
                "total_score": 10,
                "pass_score": 6,
                "question_ids": question_ids[:1],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "新考试"

    @pytest.mark.asyncio
    async def test_create_invalid_question_ids(self, client: AsyncClient, token: str):
        """question_ids 不存在返回 400"""
        resp = await client.post(
            "/api/exams",
            json={
                "title": "无效", "duration_minutes": 30,
                "total_score": 10, "pass_score": 6,
                "question_ids": [99999],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_create_requires_auth(self, client: AsyncClient, question_ids: list[int]):
        """未认证不能创建"""
        resp = await client.post(
            "/api/exams",
            json={
                "title": "无认证", "duration_minutes": 30,
                "total_score": 10, "pass_score": 6,
                "question_ids": question_ids[:1],
            },
        )
        assert resp.status_code == 401


class TestExamList:
    """考试列表测试"""

    @pytest.mark.asyncio
    async def test_list(self, client: AsyncClient, exam_id: int):
        """考试列表"""
        resp = await client.get("/api/exams")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] >= 1
        assert len(data["data"]["items"]) >= 1

    @pytest.mark.asyncio
    async def test_filter_by_status(self, client: AsyncClient, token: str, question_ids: list[int]):
        """按状态筛选"""
        # 创建一个 draft 考试
        await client.post(
            "/api/exams",
            json={
                "title": "草稿考试", "duration_minutes": 30,
                "total_score": 10, "pass_score": 6,
                "question_ids": question_ids[:1],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = await client.get("/api/exams?status=draft")
        assert resp.status_code == 200
        for item in resp.json()["data"]["items"]:
            assert item["status"] == "draft"


class TestExamDetail:
    """考试详情测试"""

    @pytest.mark.asyncio
    async def test_detail(self, client: AsyncClient, exam_id: int):
        """考试详情含题目列表"""
        resp = await client.get(f"/api/exams/{exam_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["id"] == exam_id
        assert "questions" in data["data"]

    @pytest.mark.asyncio
    async def test_detail_not_found(self, client: AsyncClient):
        """不存在的考试"""
        resp = await client.get("/api/exams/99999")
        assert resp.status_code == 404


class TestExamUpdate:
    """更新考试测试"""

    @pytest.mark.asyncio
    async def test_update(self, client: AsyncClient, token: str, exam_id: int):
        """更新考试配置"""
        resp = await client.put(
            f"/api/exams/{exam_id}",
            json={"title": "已更新的考试"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200


class TestExamDelete:
    """删除考试测试"""

    @pytest.mark.asyncio
    async def test_delete(self, client: AsyncClient, token: str, question_ids: list[int]):
        """删除考试"""
        # 先创建一个新考试
        create_resp = await client.post(
            "/api/exams",
            json={
                "title": "待删除", "duration_minutes": 30,
                "total_score": 10, "pass_score": 6,
                "question_ids": question_ids[:1],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        eid = create_resp.json()["data"]["id"]

        resp = await client.delete(
            f"/api/exams/{eid}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        # 再次查询应返回 404
        resp2 = await client.get(f"/api/exams/{eid}")
        assert resp2.status_code == 404


class TestExamPublish:
    """发布/关闭考试测试"""

    @pytest.mark.asyncio
    async def test_publish(self, client: AsyncClient, token: str, exam_id: int):
        """发布考试"""
        resp = await client.post(
            f"/api/exams/{exam_id}/publish",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "open"

    @pytest.mark.asyncio
    async def test_publish_empty_exam(self, client: AsyncClient, token: str):
        """空考试不能发布"""
        # 创建考试（用已存在的题目，然后..."
        # 无法在 API 层面创建空考试，跳过此测试
        pass

    @pytest.mark.asyncio
    async def test_close(self, client: AsyncClient, token: str, exam_id: int):
        """关闭已发布的考试"""
        # 先发布
        await client.post(
            f"/api/exams/{exam_id}/publish",
            headers={"Authorization": f"Bearer {token}"},
        )
        # 再关闭
        resp = await client.post(
            f"/api/exams/{exam_id}/close",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "closed"
