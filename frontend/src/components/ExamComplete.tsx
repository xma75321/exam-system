"use client";

import { useRouter } from "next/navigation";

interface ExamCompleteProps {
  examId: number;
  examTitle: string;
  totalQuestions: number;
  answeredCount: number;
}

export default function ExamComplete({
  examId,
  examTitle,
  totalQuestions,
  answeredCount,
}: ExamCompleteProps) {
  const router = useRouter();

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50/50 px-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-xl">
        {/* 成功图标 */}
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100">
          <svg
            className="h-10 w-10 text-emerald-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        {/* 标题 */}
        <h1 className="mb-2 text-2xl font-bold text-gray-900">考试已提交</h1>
        <p className="mb-8 text-gray-500">您的答卷已成功提交，系统正在处理中</p>

        {/* 考试信息 */}
        <div className="mb-8 rounded-lg bg-gray-50 p-4 text-left">
          <h2 className="mb-3 text-sm font-medium text-gray-700">考试信息</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">考试名称</span>
              <span className="font-medium text-gray-900 truncate ml-4">{examTitle}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">题目数量</span>
              <span className="font-medium text-gray-900">{totalQuestions} 题</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">已答题目</span>
              <span className="font-medium text-gray-900">{answeredCount} 题</span>
            </div>
          </div>
        </div>

        {/* 按钮 */}
        <div className="flex flex-col gap-3">
          <button
            type="button"
            onClick={() => router.push(`/exams/${examId}/result`)}
            className="w-full rounded-lg bg-primary-600 px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-700"
          >
            查看结果
          </button>
          <button
            type="button"
            onClick={() => router.push("/exams")}
            className="w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            返回考试列表
          </button>
        </div>
      </div>
    </div>
  );
}
