"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { attemptApi } from "@/lib/api";
import type { AttemptResult } from "@/types/exam";
import ScoreSummary from "@/components/ScoreSummary";
import TypeStats from "@/components/TypeStats";
import QuestionReview from "@/components/QuestionReview";

export default function ResultPage() {
  const params = useParams();
  const router = useRouter();
  const attemptId = Number(params.id);

  const [result, setResult] = useState<AttemptResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!attemptId) return;

    const fetchResult = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await attemptApi.getResult(attemptId);
        setResult(res.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载失败");
      } finally {
        setLoading(false);
      }
    };

    fetchResult();
  }, [attemptId]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-sm">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
            <svg
              className="h-8 w-8 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h1 className="mb-2 text-xl font-bold text-gray-900">加载失败</h1>
          <p className="mb-6 text-gray-500">{error || "无法获取考试结果"}</p>
          <button
            type="button"
            onClick={() => router.push("/exams")}
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            返回考试列表
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-3xl">
        {/* 返回按钮 */}
        <div className="mb-6">
          <button
            type="button"
            onClick={() => router.push("/exams")}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            返回考试列表
          </button>
        </div>

        {/* 标题 */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">{result.exam_title}</h1>
          <p className="mt-1 text-sm text-gray-500">
            考试结果 · {result.total_questions} 道题
          </p>
        </div>

        {/* 成绩概览 */}
        <div className="mb-6">
          <ScoreSummary
            totalScore={result.total_score ?? null}
            passScore={result.pass_score}
            totalQuestions={result.total_questions}
            correctCount={result.correct_count}
            pendingCount={result.pending_count}
            durationMinutes={result.duration_minutes}
            submittedAt={result.submitted_at}
            startedAt={result.started_at}
            isPassed={result.is_passed ?? null}
          />
        </div>

        {/* 题型统计 */}
        {result.type_stats.length > 0 && (
          <div className="mb-6">
            <TypeStats typeStats={result.type_stats} />
          </div>
        )}

        {/* 逐题回顾 */}
        <div>
          <h2 className="mb-4 text-lg font-semibold text-gray-900">逐题回顾</h2>
          <QuestionReview questions={result.questions} />
        </div>

        {/* 底部按钮 */}
        <div className="mt-8 flex justify-center">
          <button
            type="button"
            onClick={() => router.push("/exams")}
            className="rounded-lg bg-primary-600 px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-700"
          >
            返回考试列表
          </button>
        </div>
      </div>
    </div>
  );
}
