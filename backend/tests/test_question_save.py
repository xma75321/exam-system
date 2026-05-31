"""题库确认入库测试"""

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
    """注册用户并登录，返回 JWT Token"""
    await client.post(
        "/api/auth/register",
        json={
            "username": "saveuser",
            "email": "save@example.com",
            "password": "123456",
        },
    )
    login_resp = await client.post(
        "/api/auth/login",
        json={"username": "saveuser", "password": "123456"},
    )
    return login_resp.json()["data"]["access_token"]


class TestQuestionSave:
    """题目入库测试"""

    @pytest.mark.asyncio
    async def test_save_mixed_questions(self, client: AsyncClient, token: str):
        """保存混合题型试卷"""
        response = await client.post(
            "/api/upload/confirm",
            json={
                "filename": "test.docx",
                "questions": [
                    {
                        "temp_id": "q1",
                        "type": "single",
                        "content": "Python 是什么类型的语言？",
                        "options": [
                            {"label": "A", "content": "编译型"},
                            {"label": "B", "content": "解释型"},
                        ],
                        "answer": "B",
                        "score": 2.0,
                    },
                    {
                        "temp_id": "q2",
                        "type": "judge",
                        "content": "Python 是面向对象的语言。",
                        "answer": "正确",
                        "score": 1.0,
                    },
                    {
                        "temp_id": "q3",
                        "type": "fill",
                        "content": "定义函数使用 ______ 关键字。",
                        "answer": "def",
                        "score": 2.0,
                    },
                ],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["exam_id"] > 0
        assert len(data["data"]["questions"]) == 3
        assert data["data"]["questions"][0]["id"] > 0
        assert data["data"]["questions"][1]["id"] > 0

    @pytest.mark.asyncio
    async def test_save_single_choice_with_options(self, client: AsyncClient, token: str):
        """选择题选项正确关联"""
        response = await client.post(
            "/api/upload/confirm",
            json={
                "filename": "test.docx",
                "questions": [
                    {
                        "temp_id": "q1",
                        "type": "single",
                        "content": "选择题",
                        "options": [
                            {"label": "A", "content": "选项A"},
                            {"label": "B", "content": "选项B"},
                            {"label": "C", "content": "选项C"},
                        ],
                        "answer": "A",
                        "score": 3.0,
                    },
                ],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["exam_id"] > 0
        assert len(data["data"]["questions"]) == 1

    @pytest.mark.asyncio
    async def test_save_without_auth(self, client: AsyncClient):
        """未认证用户无法入库"""
        response = await client.post(
            "/api/upload/confirm",
            json={
                "filename": "test.docx",
                "questions": [],
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_created_exam_record(self, client: AsyncClient, token: str):
        """验证创建了对应的 exam 记录"""
        response = await client.post(
            "/api/upload/confirm",
            json={
                "filename": "my_exam.docx",
                "questions": [
                    {
                        "temp_id": "q1",
                        "type": "single",
                        "content": "测试题",
                        "options": [
                            {"label": "A", "content": "选项"},
                        ],
                        "answer": "A",
                        "score": 1.0,
                    },
                ],
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        data = response.json()
        exam_id = data["data"]["exam_id"]
        assert exam_id > 0
        assert data["data"]["questions"][0]["id"] > 0
