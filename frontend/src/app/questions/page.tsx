"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AlertCircle, RefreshCw } from "lucide-react";
import { questionApi } from "@/lib/api";
import { useAuthStore } from "@/hooks/useAuth";
import type { Question, QuestionType } from "@/types/question";
import QuestionFilter from "@/components/QuestionFilter";
import QuestionCard, { type QuestionCardData } from "@/components/QuestionCard";
import Pagination from "@/components/Pagination";

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-lg border border-gray-100 bg-white px-4 py-3">
      <div className="flex items-center gap-3">
        <div className="h-6 w-6 shrink-0 rounded-full bg-gray-200" />
        <div className="h-5 w-14 shrink-0 rounded-md bg-gray-200" />
        <div className="h-4 flex-1 rounded bg-gray-200" />
        <div className="h-4 w-8 shrink-0 rounded bg-gray-200" />
      </div>
    </div>
  );
}

export default function QuestionsPage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentType, setCurrentType] = useState<QuestionType | "all">("all");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [detailCache, setDetailCache] = useState<Record<number, QuestionCardData>>({});

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const fetchQuestions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await questionApi.list(
        page,
        pageSize,
        currentType === "all" ? undefined : currentType
      );
      if (res.code === 0) {
        setQuestions(res.data.items);
        setTotal(res.data.total);
      } else {
        setError(res.message || "获取题目列表失败");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "网络错误，请重试");
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, currentType]);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  const handleFilterChange = (type: QuestionType | "all") => {
    setCurrentType(type);
    setPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (newSize: number) => {
    setPageSize(newSize);
    setPage(1);
  };

  const getCardData = (question: Question, index: number): QuestionCardData => {
    if (detailCache[question.id]) {
      return detailCache[question.id];
    }
    return {
      id: question.id,
      type: question.type,
      content: question.content,
      score: question.score,
    };
  };

  const handleExpand = useCallback(
    async (questionId: number) => {
      if (detailCache[questionId]) return;

      try {
        const res = await questionApi.getDetail(questionId);
        if (res.code === 0) {
          const detail = res.data;
          setDetailCache((prev) => ({
            ...prev,
            [questionId]: {
              id: detail.id,
              type: detail.type,
              content: detail.content,
              score: detail.score,
              options: detail.options,
              answer: detail.answer,
              explanation: detail.explanation,
            },
          }));
        }
      } catch {
        // Silently fail - card will show basic info
      }
    },
    [detailCache]
  );

  const startIndex = (page - 1) * pageSize;

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-6">
            <h1 className="text-lg font-semibold text-gray-900">题库</h1>
            <nav className="flex items-center gap-1">
              <Link
                href="/exams"
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                考试列表
              </Link>
              <Link
                href="/upload"
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                上传试卷
              </Link>
              <Link
                href="/reports"
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                统计
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user?.username || "未登录"}
            </span>
            <button
              type="button"
              onClick={() => {
                logout();
                router.push("/auth");
              }}
              className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
            >
              退出登录
            </button>
            <Link
              href="/upload"
              className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-700"
            >
              上传试卷
            </Link>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-6xl px-6 py-6">
        {/* Filter bar */}
        <div className="mb-4 flex items-center justify-between">
          <QuestionFilter value={currentType} onChange={handleFilterChange} />
        </div>

        {/* Error state */}
        {error && (
          <div className="mb-4 flex items-center gap-3 rounded-lg border border-red-100 bg-red-50 px-4 py-3">
            <AlertCircle className="h-5 w-5 shrink-0 text-red-500" />
            <p className="flex-1 text-sm text-red-600">{error}</p>
            <button
              type="button"
              onClick={fetchQuestions}
              className="flex items-center gap-1 rounded-lg border border-red-200 px-3 py-1.5 text-sm text-red-600 transition-colors hover:bg-red-100"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              重试
            </button>
          </div>
        )}

        {/* Loading state */}
        {loading && (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && questions.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <svg
              className="mb-4 h-16 w-16"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714a2.25 2.25 0 00.659 1.591L19 14.5M14.25 3.104c.251.023.501.05.75.082M19 14.5l-2.47 2.47a2.25 2.25 0 01-1.591.659H9.061a2.25 2.25 0 01-1.591-.659L5 14.5m14 0V5.846a2.25 2.25 0 00-.217-1.008l-1.106-2.21A2.25 2.25 0 0015.6 2.1H8.4a2.25 2.25 0 00-2.077 1.528L5.217 5.838A2.25 2.25 0 005 6.846V14.5"
              />
            </svg>
            <p className="mb-2 text-base font-medium text-gray-500">暂无题目</p>
            <p className="mb-4 text-sm text-gray-400">上传试卷后题目将出现在这里</p>
            <Link
              href="/upload"
              className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-700"
            >
              去上传
            </Link>
          </div>
        )}

        {/* Question list */}
        {!loading && !error && questions.length > 0 && (
          <>
            <div className="space-y-2">
              {questions.map((question, i) => (
                <div
                  key={question.id}
                  onClick={() => handleExpand(question.id)}
                  role="presentation"
                >
                  <QuestionCard
                    question={getCardData(question, startIndex + i)}
                    index={startIndex + i}
                  />
                </div>
              ))}
            </div>

            <div className="mt-6">
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                total={total}
                pageSize={pageSize}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
              />
            </div>
          </>
        )}
      </main>
    </div>
  );
}