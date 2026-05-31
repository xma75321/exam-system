"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ToastProvider, useToast } from "@/components/Toast";
import QuestionDisplay from "@/components/QuestionDisplay";
import QuestionNav from "@/components/QuestionNav";
import CountdownTimer from "@/components/CountdownTimer";
import TimeWarningModal from "@/components/TimeWarningModal";
import SaveIndicator from "@/components/SaveIndicator";
import SubmitConfirmModal from "@/components/SubmitConfirmModal";
import ExamComplete from "@/components/ExamComplete";
import { useCountdown } from "@/hooks/useCountdown";
import { useAutoSave } from "@/hooks/useAutoSave";
import { attemptApi } from "@/lib/api";
import type { AttemptQuestion, AttemptStartResponse } from "@/lib/api";
import type { QuestionType } from "@/types/question";

function TakeExamPageContent() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { showToast } = useToast();

  const [attempt, setAttempt] = useState<AttemptStartResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState(false);
  const [showTimeWarning, setShowTimeWarning] = useState(false);
  const [completed, setCompleted] = useState(false);

  // 保存当前答案到服务器
  const saveToServer = useCallback(async () => {
    if (!attempt) return;

    const currentQuestion = attempt.questions[currentIndex];
    if (!currentQuestion) return;

    const answer = answers[currentQuestion.id];
    if (answer === undefined) return;

    await attemptApi.saveAnswers(attempt.id, [
      { question_id: currentQuestion.id, user_answer: answer },
    ]);
  }, [attempt, currentIndex, answers]);

  // 自动保存
  const { status: saveStatus, markDirty, saveNow, retry: retrySave } = useAutoSave({
    saveFn: saveToServer,
    interval: 30000,
  });

  // 计算结束时间
  const endTime = useMemo(() => {
    if (!attempt) return null;
    const start = new Date(attempt.started_at).getTime();
    return new Date(start + attempt.duration_minutes * 60 * 1000).toISOString();
  }, [attempt]);

  // 倒计时
  const { formattedTime, isWarning, isExpired, remainingSeconds } = useCountdown({
    endTime: endTime ?? new Date().toISOString(),
    onWarning: () => setShowTimeWarning(true),
    onExpire: () => handleSubmit(),
  });

  // 加载或开始考试
  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const examId = parseInt(id, 10);
        if (isNaN(examId)) {
          showToast("无效的考试 ID", "error");
          router.push("/exams");
          return;
        }

        // 尝试开始考试
        const res = await attemptApi.start(examId);
        setAttempt(res.data);

        // 加载已保存的答案
        const progressRes = await attemptApi.getProgress(res.data.id);
        const answered: Record<number, string> = {};
        for (const a of progressRes.data.answered) {
          answered[a.question_id] = a.user_answer;
        }
        setAnswers(answered);
      } catch (err) {
        showToast(
          err instanceof Error ? err.message : "加载考试失败",
          "error"
        );
        router.push("/exams");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id, router, showToast]);

  // 切题时保存答案
  const handleNavigate = useCallback(
    async (index: number) => {
      await saveNow();
      setCurrentIndex(index);
    },
    [saveNow]
  );

  // 答案变化
  const handleAnswerChange = useCallback(
    (answer: string) => {
      if (!attempt) return;
      const question = attempt.questions[currentIndex];
      if (!question) return;
      setAnswers((prev) => ({ ...prev, [question.id]: answer }));
      markDirty();
    },
    [attempt, currentIndex, markDirty]
  );

  // 提交考试
  const handleSubmit = useCallback(async () => {
    if (!attempt || submitting) return;

    setSubmitting(true);
    try {
      // 先保存当前答案
      await saveNow();

      // 提交考试
      await attemptApi.submit(attempt.id);
      setCompleted(true);
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "提交失败",
        "error"
      );
    } finally {
      setSubmitting(false);
      setConfirmDialog(false);
    }
  }, [attempt, submitting, saveNow, showToast]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-gray-400">
        加载中...
      </div>
    );
  }

  if (!attempt) {
    return null;
  }

  // 显示完成页面
  if (completed) {
    const answeredCount = Object.keys(answers).filter(
      (k) => answers[parseInt(k)] !== undefined && answers[parseInt(k)] !== ""
    ).length;
    return (
      <ExamComplete
        examId={attempt.exam_id}
        examTitle={attempt.exam_title}
        totalQuestions={attempt.questions.length}
        answeredCount={answeredCount}
      />
    );
  }

  const currentQuestion = attempt.questions[currentIndex];
  const answeredIds = new Set(
    attempt.questions
      .map((q, i) => (answers[q.id] ? i : -1))
      .filter((i) => i >= 0)
  );

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-6">
          <h1 className="text-base font-semibold text-gray-900 truncate">
            {attempt.exam_title}
          </h1>
          <SaveIndicator status={saveStatus} onRetry={retrySave} />
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-7xl px-6 py-6">
        <div className="flex gap-6">
          {/* 左侧：答题区 */}
          <div className="min-w-0 flex-1">
            {currentQuestion && (
              <QuestionDisplay
                question={{
                  ...currentQuestion,
                  type: currentQuestion.type as QuestionType,
                }}
                currentIndex={currentIndex}
                total={attempt.questions.length}
                answer={answers[currentQuestion.id] ?? ""}
                onAnswerChange={handleAnswerChange}
              />
            )}
          </div>

          {/* 右侧：计时器 + 导航 */}
          <div className="w-64 shrink-0 space-y-4">
            {endTime && (
              <CountdownTimer
                formattedTime={formattedTime}
                isWarning={isWarning}
                isExpired={isExpired}
              />
            )}
            <QuestionNav
              total={attempt.questions.length}
              currentIndex={currentIndex}
              answeredIds={answeredIds}
              onNavigate={handleNavigate}
              onSubmit={() => setConfirmDialog(true)}
              submitting={submitting}
            />
          </div>
        </div>
      </main>

      {/* 时间警告弹窗 */}
      <TimeWarningModal
        open={showTimeWarning && !isExpired}
        remainingSeconds={remainingSeconds}
        onClose={() => setShowTimeWarning(false)}
        onSubmit={handleSubmit}
        submitting={submitting}
      />

      {/* 提交确认弹窗 */}
      <SubmitConfirmModal
        open={confirmDialog}
        totalQuestions={attempt.questions.length}
        answeredCount={answeredIds.size}
        submitting={submitting}
        onConfirm={handleSubmit}
        onCancel={() => setConfirmDialog(false)}
      />
    </div>
  );
}

export default function TakeExamPage() {
  return (
    <ToastProvider>
      <TakeExamPageContent />
    </ToastProvider>
  );
}
