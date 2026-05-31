"""手动评分测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.models.exam import Exam, Question
from app.models.attempt import ExamAttempt, QuestionResponse
from app.utils.security import get_password_hash


@pytest.fixture
def db():
    """创建数据库会话"""
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as session:
        yield session
    engine.dispose()


def setup_test_data(db: Session, username: str = "test_manual_grade"):
    """创建测试数据"""
    # 创建用户（使用真正的密码哈希）
    user = User(
        username=username,
        email=f"{username}@example.com",
        password_hash=get_password_hash("Test123456"),
    )
    db.add(user)
    db.flush()

    # 创建考试
    exam = Exam(
        title="手动评分测试",
        duration_minutes=60,
        total_score=100,
        pass_score=60,
        status="open",
        created_by=user.id,
    )
    db.add(exam)
    db.flush()

    # 创建简答题
    question = Question(
        exam_id=exam.id,
        type="essay",
        content="请简述 Python 的特点",
        answer="参考答案：简洁、易读、跨平台",
        score=40,
        sort_order=1,
    )
    db.add(question)
    db.flush()

    # 创建作答记录
    attempt = ExamAttempt(
        exam_id=exam.id,
        user_id=user.id,
        status="submitted",
    )
    db.add(attempt)
    db.flush()

    # 创建作答
    response = QuestionResponse(
        attempt_id=attempt.id,
        question_id=question.id,
        user_answer="Python 是一种简洁易读的编程语言",
        graded_by="pending",
    )
    db.add(response)
    db.commit()

    return user, exam, question, attempt, response


@pytest.mark.asyncio
async def test_manual_grade_essay_success(client: AsyncClient):
    """手动评分简答题成功"""
    db_engine = create_engine(settings.DATABASE_URL)
    with Session(db_engine) as db:
        user, exam, question, attempt, response = setup_test_data(db, "test_grade_success")
        response_id = response.id

    # 登录
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "test_grade_success", "password": "Test123456"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]

    # 手动评分
    res = await client.put(
        f"/api/responses/{response_id}/score",
        json={"score": 35, "comment": "回答较好"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["score"] == 35.0
    assert data["graded_by"] == "manual"


@pytest.mark.asyncio
async def test_manual_grade_score_exceeds_limit(client: AsyncClient):
    """分值超过上限返回 400"""
    db_engine = create_engine(settings.DATABASE_URL)
    with Session(db_engine) as db:
        user, exam, question, attempt, response = setup_test_data(db, "test_grade_limit")
        response_id = response.id

    # 登录
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "test_grade_limit", "password": "Test123456"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]

    # 尝试评分超过上限（题目分值是 40）
    res = await client.put(
        f"/api/responses/{response_id}/score",
        json={"score": 50},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_manual_grade_non_essay_forbidden(client: AsyncClient):
    """非简答题不能手动评分"""
    db_engine = create_engine(settings.DATABASE_URL)
    with Session(db_engine) as db:
        # 创建用户
        user = User(
            username="test_grade_nonessay",
            email="test_grade_nonessay@example.com",
            password_hash=get_password_hash("Test123456"),
        )
        db.add(user)
        db.flush()

        # 创建考试
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

        # 创建单选题
        question = Question(
            exam_id=exam.id,
            type="single",
            content="单选题",
            answer="A",
            score=10,
            sort_order=1,
        )
        db.add(question)
        db.flush()

        # 创建作答记录
        attempt = ExamAttempt(
            exam_id=exam.id,
            user_id=user.id,
            status="submitted",
        )
        db.add(attempt)
        db.flush()

        # 创建作答
        response = QuestionResponse(
            attempt_id=attempt.id,
            question_id=question.id,
            user_answer="A",
            graded_by="auto",
        )
        db.add(response)
        db.commit()
        response_id = response.id

    # 登录
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "test_grade_nonessay", "password": "Test123456"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]

    # 尝试手动评分非简答题
    res = await client.put(
        f"/api/responses/{response_id}/score",
        json={"score": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert "简答题" in res.json()["detail"]["message"]


@pytest.mark.asyncio
async def test_manual_grade_updates_total_score(client: AsyncClient):
    """评分后总分重新计算"""
    db_engine = create_engine(settings.DATABASE_URL)
    with Session(db_engine) as db:
        user, exam, question, attempt, response = setup_test_data(db, "test_grade_total")
        response_id = response.id
        attempt_id = attempt.id

    # 登录
    login_res = await client.post(
        "/api/auth/login",
        json={"username": "test_grade_total", "password": "Test123456"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]

    # 手动评分
    res = await client.put(
        f"/api/responses/{response_id}/score",
        json={"score": 35},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["total_score"] == 35.0
    assert data["attempt_status"] == "graded"
