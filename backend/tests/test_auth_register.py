"""用户注册 API 测试"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """创建测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """正常注册返回 201"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "123456",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["username"] == "newuser"
    assert data["data"]["email"] == "newuser@example.com"
    assert "id" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """重复用户名返回 400"""
    # 先注册一个用户
    await client.post(
        "/api/auth/register",
        json={
            "username": "dupuser",
            "email": "dup@example.com",
            "password": "123456",
        },
    )
    # 重复注册
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "dupuser",
            "email": "other@example.com",
            "password": "123456",
        },
    )
    assert response.status_code == 400
    assert "用户名已被注册" in response.json()["detail"]["message"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """重复邮箱返回 400"""
    await client.post(
        "/api/auth/register",
        json={
            "username": "emailuser1",
            "email": "same@example.com",
            "password": "123456",
        },
    )
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "emailuser2",
            "email": "same@example.com",
            "password": "123456",
        },
    )
    assert response.status_code == 400
    assert "邮箱已被注册" in response.json()["detail"]["message"]


@pytest.mark.asyncio
async def test_register_short_username(client: AsyncClient):
    """用户名过短返回 422"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "ab",
            "email": "short@example.com",
            "password": "123456",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    """密码过短返回 422"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "validuser",
            "email": "valid@example.com",
            "password": "12345",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """邮箱格式错误返回 422"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "validuser",
            "email": "not-an-email",
            "password": "123456",
        },
    )
    assert response.status_code == 422
