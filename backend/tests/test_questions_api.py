"""题库查询 API 测试"""

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
    """注册用户并登录，返回 Token"""
    await client.post(
        "/api/auth/register",
        json={"username": "quser", "email": "q@test.com", "password": "123456"},
    )
    resp = await client.post(
        "/api/auth/login",
        json={"username": "quser", "password": "123456"},
    )
    return resp.json()["data"]["access_token"]


@pytest.fixture
async def saved_question_id(client: AsyncClient, token: str) -> int:
    """创建一条测试题目并返回 ID"""
    resp = await client.post(
        "/api/upload/confirm",
        json={
            "filename": "test.docx",
            "questions": [
                {
                    "temp_id": "q1",
                    "type": "single",
                    "content": "测试单选题",
                    "options": [
                        {"label": "A", "content": "选项A"},
                        {"label": "B", "content": "选项B"},
                    ],
                    "answer": "A",
                    "score": 2.0,
                },
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["data"]["questions"][0]["id"]


class TestQuestionList:
    """题目列表测试"""

    @pytest.mark.asyncio
    async def test_list_all(self, client: AsyncClient, token: str, saved_question_id: int):
        """获取全部题目列表"""
        resp = await client.get("/api/questions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1
        assert len(data["data"]["items"]) >= 1

    @pytest.mark.asyncio
    async def test_filter_by_type(self, client: AsyncClient, token: str, saved_question_id: int):
        """按题型筛选"""
        resp = await client.get("/api/questions?type=single")
        assert resp.status_code == 200
        data = resp.json()
        for item in data["data"]["items"]:
            assert item["type"] == "single"

    @pytest.mark.asyncio
    async def test_pagination(self, client: AsyncClient, token: str):
        """分页功能"""
        resp = await client.get("/api/questions?page=1&page_size=1")
        data = resp.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 1
        assert len(data["data"]["items"]) <= 1

    @pytest.mark.asyncio
    async def test_detail(self, client: AsyncClient, saved_question_id: int):
        """获取题目详情（含选项）"""
        resp = await client.get(f"/api/questions/{saved_question_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["type"] == "single"
        assert data["data"]["answer"] == "A"
        assert len(data["data"]["options"]) == 2

    @pytest.mark.asyncio
    async def test_detail_not_found(self, client: AsyncClient):
        """查询不存在的题目返回 404"""
        resp = await client.get("/api/questions/99999")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete(self, client: AsyncClient, token: str, saved_question_id: int):
        """删除题目"""
        resp = await client.delete(
            f"/api/questions/{saved_question_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["message"] == "删除成功"

        # 再次查询应返回 404
        resp2 = await client.get(f"/api/questions/{saved_question_id}")
        assert resp2.status_code == 404
