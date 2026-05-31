"""测试公共 fixtures"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.main import app
from app.config import settings
from app.database import Base, get_db


@pytest.fixture
async def client():
    """创建测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def cleanup_test_users():
    """每个测试前后清理测试数据"""
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as db:
        # 删除所有测试用户（username 包含 "test" 或以特定前缀开头）
        from app.models.user import User
        from app.models.attempt import QuestionResponse, ExamAttempt
        from app.models.exam import Option, Question, Exam

        # 级联清理（按依赖顺序）
        db.query(QuestionResponse).delete()
        db.query(ExamAttempt).delete()
        db.query(Option).delete()
        db.query(Question).delete()
        db.query(Exam).delete()
        db.query(User).delete()
        db.commit()
    yield
    # 测试后同样清理
    with Session(engine) as db:
        from app.models.user import User
        from app.models.attempt import QuestionResponse, ExamAttempt
        from app.models.exam import Option, Question, Exam

        db.query(QuestionResponse).delete()
        db.query(ExamAttempt).delete()
        db.query(Option).delete()
        db.query(Question).delete()
        db.query(Exam).delete()
        db.query(User).delete()
        db.commit()
    engine.dispose()
