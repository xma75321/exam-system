"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useToast } from "@/components/Toast";
import { useAuthStore } from "@/hooks/useAuth";
import { examApi } from "@/lib/api";
import type { ExamResponse } from "@/types/exam";

export default function ExamDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { showToast } = useToast();
  const { user, logout } = useAuthStore();
  const [exam, setExam] = useState<ExamResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const examId = Number(params.id);

  const loadExam = useCallback(async () => {
    try {
      const res = await examApi.list(1, 100);
      const found = res.data.items.find((e) => e.id === examId);
      if (found) {
        setExam(found);
      } else {
        showToast("考试不存在", "error");
        router.push("/exams");
      }
    } catch (err) {
      showToast("加载失败", "error");
    } finally {
      setLoading(false);
    }
  }, [examId, router, showToast]);

  useEffect(() => {
    loadExam();
  }, [loadExam]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-gray-400">
        加载中...
      </div>
    );
  }

  if (!exam) return null;

  return (
    <div className="min-h-screen bg-gray-50/50">
      <header className="border-b border-gray-100 bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-6">
            <h1 className="text-lg font-semibold text-gray-900">考试详情</h1>
            <nav className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => router.push("/exams")}
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                考试列表
              </button>
              <button
                type="button"
                onClick={() => router.push("/upload")}
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                上传试卷
              </button>
              <button
                type="button"
                onClick={() => router.push("/questions")}
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                题库
              </button>
              <button
                type="button"
                onClick={() => router.push("/reports")}
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                统计
              </button>
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
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-bold text-gray-900">{exam.title}</h2>
          
          {exam.description && (
            <p className="mb-6 text-gray-600">{exam.description}</p>
          )}

          <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg bg-gray-50 p-4">
              <div className="text-sm text-gray-500">题目数量</div>
              <div className="mt-1 text-2xl font-semibold">{exam.question_count}</div>
            </div>
            <div className="rounded-lg bg-gray-50 p-4">
              <div className="text-sm text-gray-500">考试时长</div>
              <div className="mt-1 text-2xl font-semibold">{exam.duration_minutes} 分钟</div>
            </div>
            <div className="rounded-lg bg-gray-50 p-4">
              <div className="text-sm text-gray-500">总分</div>
              <div className="mt-1 text-2xl font-semibold">{exam.total_score} 分</div>
            </div>
            <div className="rounded-lg bg-gray-50 p-4">
              <div className="text-sm text-gray-500">及格分</div>
              <div className="mt-1 text-2xl font-semibold">{exam.pass_score} 分</div>
            </div>
          </div>

          <div className="flex gap-3">
            {exam.status === "open" && (
              <button
                type="button"
                onClick={() => router.push(`/exams/${exam.id}/take`)}
                className="rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-primary-700"
              >
                开始考试
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
