"""答题 API 路由"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.attempt import ExamAttempt
from app.models.exam import Question, Option
from app.schemas.attempt import (
    AttemptStart,
    AttemptResponse,
    AnswerSave,
    AttemptProgressResponse,
    QuestionInAttempt,
    OptionInAttempt,
    AnsweredQuestion,
    AttemptResultResponse,
    QuestionResult,
    TypeStat,
)
from app.services.attempt_service import (
    start_exam,
    get_attempt,
    save_answers,
    submit_exam,
    get_question_with_options,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/attempts", tags=["答题"])


@router.post(
    "",
    response_model=dict,
    status_code=201,
    summary="开始考试",
)
def start(
    body: AttemptStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """开始考试，创建作答记录。"""
    try:
        attempt = start_exam(db, body.exam_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": 1001, "message": str(e)},
        )

    # 构建响应
    from app.models.exam import Exam

    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    questions = (
        db.query(Question)
        .filter(Question.exam_id == attempt.exam_id)
        .order_by(Question.sort_order)
        .all()
    )

    question_list = []
    for q in questions:
        options = (
            db.query(Option)
            .filter(Option.question_id == q.id)
            .order_by(Option.id)
            .all()
        )
        question_list.append(
            QuestionInAttempt(
                id=q.id,
                type=q.type,
                content=q.content,
                score=float(q.score),
                sort_order=q.sort_order,
                options=[
                    OptionInAttempt(id=o.id, label=o.label, content=o.content)
                    for o in options
                ]
                if options
                else None,
            )
        )

    return {
        "code": 0,
        "data": AttemptResponse(
            id=attempt.id,
            exam_id=attempt.exam_id,
            exam_title=exam.title,
            status=attempt.status,
            started_at=attempt.started_at,
            duration_minutes=exam.duration_minutes,
            end_time=None,
            questions=question_list,
        ).model_dump(),
        "message": "考试已开始",
    }


@router.get(
    "/{attempt_id}",
    response_model=dict,
    summary="获取答题进度",
)
def get_progress(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取作答进度和已保存的答案。"""
    result = get_attempt(db, attempt_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "作答记录不存在"},
        )

    attempt, exam, questions, answers_map = result

    # 验证权限
    if attempt.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": 403, "message": "无权访问此作答记录"},
        )

    question_list = []
    for q in questions:
        options = (
            db.query(Option)
            .filter(Option.question_id == q.id)
            .order_by(Option.id)
            .all()
        )
        question_list.append(
            QuestionInAttempt(
                id=q.id,
                type=q.type,
                content=q.content,
                score=float(q.score),
                sort_order=q.sort_order,
                options=[
                    OptionInAttempt(id=o.id, label=o.label, content=o.content)
                    for o in options
                ]
                if options
                else None,
            )
        )

    answered = [
        AnsweredQuestion(question_id=qid, user_answer=ans)
        for qid, ans in answers_map.items()
        if ans is not None
    ]

    return {
        "code": 0,
        "data": AttemptProgressResponse(
            id=attempt.id,
            exam_id=attempt.exam_id,
            exam_title=exam.title,
            status=attempt.status,
            started_at=attempt.started_at,
            duration_minutes=exam.duration_minutes,
            end_time=None,
            questions=question_list,
            answered=answered,
        ).model_dump(),
        "message": "success",
    }


@router.put(
    "/{attempt_id}/answers",
    response_model=dict,
    summary="保存答案",
)
def save(
    attempt_id: int,
    body: AnswerSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """保存用户答案。"""
    # 验证作答记录存在
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "作答记录不存在"},
        )

    # 验证权限
    if attempt.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": 403, "message": "无权操作此作答记录"},
        )

    try:
        save_answers(
            db,
            attempt_id,
            [{"question_id": a.question_id, "user_answer": a.user_answer} for a in body.answers],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": 1001, "message": str(e)},
        )

    return {
        "code": 0,
        "data": None,
        "message": "答案已保存",
    }


@router.post(
    "/{attempt_id}/submit",
    response_model=dict,
    summary="提交考试",
)
def submit(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """提交考试。"""
    # 验证作答记录存在
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "作答记录不存在"},
        )

    # 验证权限
    if attempt.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": 403, "message": "无权操作此作答记录"},
        )

    try:
        attempt = submit_exam(db, attempt_id)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": 1001, "message": str(e)},
        )

    return {
        "code": 0,
        "data": {
            "id": attempt.id,
            "status": attempt.status,
            "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        },
        "message": "考试已提交",
    }


@router.get(
    "/{attempt_id}/result",
    response_model=dict,
    summary="获取考试结果",
)
def get_result(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取考试结果详情，包含正确答案和得分。"""
    from app.models.attempt import QuestionResponse
    from app.models.exam import Exam

    # 获取作答记录
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "作答记录不存在"},
        )

    # 验证权限
    if attempt.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail={"code": 403, "message": "无权访问此作答记录"},
        )

    # 只有已评分的才能查看结果
    if attempt.status not in ("submitted", "graded"):
        raise HTTPException(
            status_code=400,
            detail={"code": 1001, "message": "考试尚未完成评分"},
        )

    # 获取考试信息
    exam = db.query(Exam).filter(Exam.id == attempt.exam_id).first()
    if exam is None:
        raise HTTPException(
            status_code=404,
            detail={"code": 404, "message": "考试不存在"},
        )

    # 获取题目和作答
    questions = (
        db.query(Question)
        .filter(Question.exam_id == attempt.exam_id)
        .order_by(Question.sort_order)
        .all()
    )

    responses = (
        db.query(QuestionResponse)
        .filter(QuestionResponse.attempt_id == attempt_id)
        .all()
    )
    response_map = {r.question_id: r for r in responses}

    # 构建结果列表
    question_results = []
    correct_count = 0
    pending_count = 0
    type_stats_map: dict[str, dict] = {}

    for q in questions:
        response = response_map.get(q.id)
        options = (
            db.query(Option)
            .filter(Option.question_id == q.id)
            .order_by(Option.id)
            .all()
        )

        user_answer = response.user_answer if response else None
        earned_score = float(response.score) if response and response.score is not None else None
        is_correct = response.is_correct if response else None

        # 统计
        if q.type not in type_stats_map:
            type_stats_map[q.type] = {"type": q.type, "total": 0, "correct": 0, "pending": 0}
        type_stats_map[q.type]["total"] += 1
        if is_correct:
            type_stats_map[q.type]["correct"] += 1
            correct_count += 1
        elif response and response.graded_by == "pending":
            type_stats_map[q.type]["pending"] += 1
            pending_count += 1

        question_results.append(
            QuestionResult(
                id=q.id,
                type=q.type,
                content=q.content,
                score=float(q.score),
                sort_order=q.sort_order,
                options=[
                    OptionInAttempt(id=o.id, label=o.label, content=o.content)
                    for o in options
                ]
                if options
                else None,
                user_answer=user_answer,
                correct_answer=q.answer or "",
                earned_score=earned_score,
                is_correct=is_correct,
                explanation=q.explanation,
            )
        )

    type_stats = [TypeStat(**v) for v in type_stats_map.values()]

    # 计算是否及格
    total_score = float(attempt.total_score) if attempt.total_score is not None else None
    is_passed = total_score >= exam.pass_score if total_score is not None else None

    return {
        "code": 0,
        "data": AttemptResultResponse(
            id=attempt.id,
            exam_id=attempt.exam_id,
            exam_title=exam.title,
            status=attempt.status,
            started_at=attempt.started_at,
            submitted_at=attempt.submitted_at,
            duration_minutes=exam.duration_minutes,
            total_score=total_score,
            objective_score=float(attempt.objective_score) if attempt.objective_score else None,
            subjective_score=float(attempt.subjective_score) if attempt.subjective_score else None,
            pass_score=exam.pass_score,
            total_questions=len(questions),
            correct_count=correct_count,
            pending_count=pending_count,
            is_passed=is_passed,
            questions=question_results,
            type_stats=type_stats,
        ).model_dump(),
        "message": "success",
    }
