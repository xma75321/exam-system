"""评分服务测试"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.models.exam import Exam, Question
from app.models.attempt import ExamAttempt, QuestionResponse
from app.services.grade_service import (
    grade_attempt,
    grade_single_choice,
    grade_multi_choice,
    grade_judge,
    grade_fill,
)


@pytest.fixture
def db():
    """创建数据库会话"""
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as session:
        yield session
    engine.dispose()


def create_test_data(db: Session):
    """创建测试数据"""
    # 创建用户
    user = User(
        username="test_grade_user",
        email="test_grade@example.com",
        password_hash="hashed_password",
    )
    db.add(user)
    db.flush()

    # 创建考试
    exam = Exam(
        title="评分测试考试",
        duration_minutes=60,
        total_score=100,
        pass_score=60,
        status="open",
        created_by=user.id,
    )
    db.add(exam)
    db.flush()

    # 创建题目
    questions = [
        Question(
            exam_id=exam.id,
            type="single",
            content="单选题",
            answer="A",
            score=10,
            sort_order=1,
        ),
        Question(
            exam_id=exam.id,
            type="multi",
            content="多选题",
            answer="A,B,C",
            score=20,
            sort_order=2,
        ),
        Question(
            exam_id=exam.id,
            type="judge",
            content="判断题",
            answer="正确",
            score=10,
            sort_order=3,
        ),
        Question(
            exam_id=exam.id,
            type="fill",
            content="填空题",
            answer="Python;编程语言",
            score=20,
            sort_order=4,
        ),
        Question(
            exam_id=exam.id,
            type="essay",
            content="简答题",
            answer="参考答案",
            score=40,
            sort_order=5,
        ),
    ]
    for q in questions:
        db.add(q)
    db.flush()

    # 创建作答记录
    attempt = ExamAttempt(
        exam_id=exam.id,
        user_id=user.id,
        status="submitted",
    )
    db.add(attempt)
    db.flush()

    return user, exam, questions, attempt


def cleanup_test_data(db: Session):
    """清理测试数据"""
    db.query(QuestionResponse).delete()
    db.query(ExamAttempt).delete()
    db.query(Question).delete()
    db.query(Exam).delete()
    db.query(User).delete()
    db.commit()


def test_grade_single_choice_correct():
    """单选题答对得满分"""
    assert grade_single_choice("A", "A") == True


def test_grade_single_choice_wrong():
    """单选题答错得 0 分"""
    assert grade_single_choice("B", "A") == False


def test_grade_multi_choice_correct():
    """多选题全对得满分"""
    assert grade_multi_choice("A,B,C", "A,B,C") == True


def test_grade_multi_choice_missing():
    """多选题漏选不得分"""
    assert grade_multi_choice("A,B", "A,B,C") == False


def test_grade_multi_choice_extra():
    """多选题多选不得分"""
    assert grade_multi_choice("A,B,C,D", "A,B,C") == False


def test_grade_multi_choice_wrong():
    """多选题答错不得分"""
    assert grade_multi_choice("D,E", "A,B,C") == False


def test_grade_judge_correct():
    """判断题答对得满分"""
    assert grade_judge("正确", "正确") == True


def test_grade_judge_wrong():
    """判断题答错得 0 分"""
    assert grade_judge("错误", "正确") == False


def test_grade_fill_correct():
    """填空题答对得满分"""
    assert grade_fill("Python;编程语言", "Python;编程语言") == True


def test_grade_fill_case_insensitive():
    """填空题忽略大小写"""
    assert grade_fill("python;编程语言", "Python;编程语言") == True


def test_grade_fill_trim():
    """填空题忽略首尾空格"""
    assert grade_fill(" Python ; 编程语言 ", "Python;编程语言") == True


def test_grade_fill_wrong():
    """填空题答错得 0 分"""
    assert grade_fill("Java;编程语言", "Python;编程语言") == False


def test_grade_attempt_success(db: Session):
    """混合题型评分总分计算"""
    try:
        user, exam, questions, attempt = create_test_data(db)

        # 创建作答记录
        responses = [
            QuestionResponse(
                attempt_id=attempt.id,
                question_id=questions[0].id,
                user_answer="A",
            ),
            QuestionResponse(
                attempt_id=attempt.id,
                question_id=questions[1].id,
                user_answer="A,B,C",
            ),
            QuestionResponse(
                attempt_id=attempt.id,
                question_id=questions[2].id,
                user_answer="正确",
            ),
            QuestionResponse(
                attempt_id=attempt.id,
                question_id=questions[3].id,
                user_answer="Python;编程语言",
            ),
            QuestionResponse(
                attempt_id=attempt.id,
                question_id=questions[4].id,
                user_answer="我的答案",
            ),
        ]
        for r in responses:
            db.add(r)
        db.commit()

        # 评分
        graded_attempt = grade_attempt(db, attempt.id)

        # 验证
        assert graded_attempt.status == "graded"
        assert graded_attempt.total_score == 60  # 10 + 20 + 10 + 20 + 0 (essay pending)
        assert graded_attempt.objective_score == 60

    finally:
        cleanup_test_data(db)


def test_grade_attempt_essay_pending(db: Session):
    """简答题标记为 pending"""
    try:
        user, exam, questions, attempt = create_test_data(db)

        # 创建简答题作答
        response = QuestionResponse(
            attempt_id=attempt.id,
            question_id=questions[4].id,
            user_answer="我的答案",
        )
        db.add(response)
        db.commit()

        # 评分
        grade_attempt(db, attempt.id)

        # 验证简答题状态
        essay_response = (
            db.query(QuestionResponse)
            .filter(
                QuestionResponse.attempt_id == attempt.id,
                QuestionResponse.question_id == questions[4].id,
            )
            .first()
        )
        assert essay_response.graded_by == "pending"
        assert essay_response.score is None
        assert essay_response.is_correct is None

    finally:
        cleanup_test_data(db)


def test_grade_attempt_already_graded(db: Session):
    """重复评分处理"""
    try:
        user, exam, questions, attempt = create_test_data(db)

        # 创建作答
        response = QuestionResponse(
            attempt_id=attempt.id,
            question_id=questions[0].id,
            user_answer="A",
        )
        db.add(response)
        db.commit()

        # 第一次评分
        grade_attempt(db, attempt.id)

        # 第二次评分（应成功）
        graded_attempt = grade_attempt(db, attempt.id)
        assert graded_attempt.status == "graded"

    finally:
        cleanup_test_data(db)
