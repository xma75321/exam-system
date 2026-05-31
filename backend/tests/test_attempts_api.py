"""答题 API 测试"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_start_exam_success(client: AsyncClient):
    """开始考试成功"""
    # 注册并登录
    await client.post(
        "/api/auth/register",
        json={
            "username": "testuser_attempts",
            "email": "test_attempts@example.com",
            "password": "password123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "testuser_attempts", "password": "password123"},
    )
    token = login_res.json()["data"]["access_token"]

    # 创建考试（通过直接插入数据库）
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.exam import Exam, Question
    from app.models.user import User

    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        user = db.query(User).filter(User.username == "testuser_attempts").first()
        exam = Exam(
            title="测试考试",
            duration_minutes=60,
            total_score=100,
            pass_score=60,
            status="open",
            created_by=user.id,
        )
        db.add(exam)
        db.flush()

        question = Question(
            exam_id=exam.id,
            type="single",
            content="测试题目",
            answer="A",
            score=10,
            sort_order=1,
        )
        db.add(question)
        db.commit()
        exam_id = exam.id

    # 开始考试
    res = await client.post(
        "/api/attempts",
        json={"exam_id": exam_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["exam_id"] == exam_id
    assert data["status"] == "in_progress"
    assert len(data["questions"]) == 1


@pytest.mark.asyncio
async def test_start_exam_already_attempted(client: AsyncClient):
    """重复参加同一考试返回 400"""
    # 注册并登录
    await client.post(
        "/api/auth/register",
        json={
            "username": "testuser_dup",
            "email": "test_dup@example.com",
            "password": "password123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "testuser_dup", "password": "password123"},
    )
    token = login_res.json()["data"]["access_token"]

    # 创建考试
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.exam import Exam, Question
    from app.models.user import User

    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        user = db.query(User).filter(User.username == "testuser_dup").first()
        exam = Exam(
            title="测试考试2",
            duration_minutes=60,
            total_score=100,
            pass_score=60,
            status="open",
            created_by=user.id,
        )
        db.add(exam)
        db.flush()

        question = Question(
            exam_id=exam.id,
            type="single",
            content="测试题目2",
            answer="A",
            score=10,
            sort_order=1,
        )
        db.add(question)
        db.commit()
        exam_id = exam.id

    # 第一次开始考试
    await client.post(
        "/api/attempts",
        json={"exam_id": exam_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 第二次开始考试（应失败）
    res = await client.post(
        "/api/attempts",
        json={"exam_id": exam_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "已参加过" in res.json()["detail"]["message"]


@pytest.mark.asyncio
async def test_start_exam_not_open(client: AsyncClient):
    """考试未开放时不能参加"""
    # 注册并登录
    await client.post(
        "/api/auth/register",
        json={
            "username": "testuser_draft",
            "email": "test_draft@example.com",
            "password": "password123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "testuser_draft", "password": "password123"},
    )
    token = login_res.json()["data"]["access_token"]

    # 创建草稿考试
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.exam import Exam
    from app.models.user import User

    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        user = db.query(User).filter(User.username == "testuser_draft").first()
        exam = Exam(
            title="草稿考试",
            duration_minutes=60,
            total_score=100,
            pass_score=60,
            status="draft",
            created_by=user.id,
        )
        db.add(exam)
        db.commit()
        exam_id = exam.id

    # 尝试开始考试（应失败）
    res = await client.post(
        "/api/attempts",
        json={"exam_id": exam_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "未开放" in res.json()["detail"]["message"]


@pytest.mark.asyncio
async def test_save_answers_success(client: AsyncClient):
    """保存答案成功"""
    # 注册并登录
    await client.post(
        "/api/auth/register",
        json={
            "username": "testuser_save",
            "email": "test_save@example.com",
            "password": "password123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "testuser_save", "password": "password123"},
    )
    token = login_res.json()["data"]["access_token"]

    # 创建考试和题目
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.exam import Exam, Question
    from app.models.user import User

    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        user = db.query(User).filter(User.username == "testuser_save").first()
        exam = Exam(
            title="保存答案测试",
            duration_minutes=60,
            total_score=100,
            pass_score=60,
            status="open",
            created_by=user.id,
        )
        db.add(exam)
        db.flush()

        question = Question(
            exam_id=exam.id,
            type="single",
            content="测试题目",
            answer="A",
            score=10,
            sort_order=1,
        )
        db.add(question)
        db.commit()
        exam_id = exam.id
        question_id = question.id

    # 开始考试
    start_res = await client.post(
        "/api/attempts",
        json={"exam_id": exam_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    attempt_id = start_res.json()["data"]["id"]

    # 保存答案
    res = await client.put(
        f"/api/attempts/{attempt_id}/answers",
        json={"answers": [{"question_id": question_id, "user_answer": "B"}]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["message"] == "答案已保存"


@pytest.mark.asyncio
async def test_submit_exam_success(client: AsyncClient):
    """提交考试成功"""
    # 注册并登录
    await client.post(
        "/api/auth/register",
        json={
            "username": "testuser_submit",
            "email": "test_submit@example.com",
            "password": "password123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "testuser_submit", "password": "password123"},
    )
    token = login_res.json()["data"]["access_token"]

    # 创建考试和题目
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.exam import Exam, Question
    from app.models.user import User

    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        user = db.query(User).filter(User.username == "testuser_submit").first()
        exam = Exam(
            title="提交考试测试",
            duration_minutes=60,
            total_score=100,
            pass_score=60,
            status="open",
            created_by=user.id,
        )
        db.add(exam)
        db.flush()

        question = Question(
            exam_id=exam.id,
            type="single",
            content="测试题目",
            answer="A",
            score=10,
            sort_order=1,
        )
        db.add(question)
        db.commit()
        exam_id = exam.id

    # 开始考试
    start_res = await client.post(
        "/api/attempts",
        json={"exam_id": exam_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    attempt_id = start_res.json()["data"]["id"]

    # 提交考试
    res = await client.post(
        f"/api/attempts/{attempt_id}/submit",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    # 提交后自动评分，状态变为 graded
    assert data["status"] in ("submitted", "graded")
    assert data["submitted_at"] is not None


@pytest.mark.asyncio
async def test_cannot_save_after_submit(client: AsyncClient):
    """提交后不能再保存答案"""
    # 注册并登录
    await client.post(
        "/api/auth/register",
        json={
            "username": "testuser_after",
            "email": "test_after@example.com",
            "password": "password123",
        },
    )
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "testuser_after", "password": "password123"},
    )
    token = login_res.json()["data"]["access_token"]

    # 创建考试和题目
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from app.config import settings
    from app.models.exam import Exam, Question
    from app.models.user import User

    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        user = db.query(User).filter(User.username == "testuser_after").first()
        exam = Exam(
            title="提交后保存测试",
            duration_minutes=60,
            total_score=100,
            pass_score=60,
            status="open",
            created_by=user.id,
        )
        db.add(exam)
        db.flush()

        question = Question(
            exam_id=exam.id,
            type="single",
            content="测试题目",
            answer="A",
            score=10,
            sort_order=1,
        )
        db.add(question)
        db.commit()
        exam_id = exam.id
        question_id = question.id

    # 开始考试
    start_res = await client.post(
        "/api/attempts",
        json={"exam_id": exam_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    attempt_id = start_res.json()["data"]["id"]

    # 提交考试
    await client.post(
        f"/api/attempts/{attempt_id}/submit",
        headers={"Authorization": f"Bearer {token}"},
    )

    # 尝试保存答案（应失败）
    res = await client.put(
        f"/api/attempts/{attempt_id}/answers",
        json={"answers": [{"question_id": question_id, "user_answer": "B"}]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "已提交" in res.json()["detail"]["message"]
