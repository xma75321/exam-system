"""用户登录 API 测试"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """创建测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def registered_user(client: AsyncClient):
    """注册一个测试用户，返回用户名和密码"""
    await client.post(
        "/api/auth/register",
        json={
            "username": "logintest",
            "email": "logintest@example.com",
            "password": "test123456",
        },
    )
    return {"username": "logintest", "password": "test123456"}


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, registered_user: dict):
    """正确凭据登录返回 200 和 Token"""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, registered_user: dict):
    """错误密码返回 401"""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": registered_user["username"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """不存在的用户返回 401"""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "nouser",
            "password": "123456",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_token(client: AsyncClient, registered_user: dict):
    """带有效 Token 访问 /me 返回用户信息"""
    # 先登录获取 Token
    login_resp = await client.post(
        "/api/auth/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    token = login_resp.json()["data"]["access_token"]

    # 使用 Token 访问 /me
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["username"] == registered_user["username"]


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
    """无 Token 访问 /me 返回 401"""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token(client: AsyncClient):
    """无效 Token 访问 /me 返回 401"""
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    assert response.status_code == 401
