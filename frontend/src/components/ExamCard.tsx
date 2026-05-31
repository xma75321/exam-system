"use client";

import type { ExamResponse, ExamStatus } from "@/types/exam";
import StatusBadge from "./StatusBadge";

interface ExamCardProps {
  exam: ExamResponse;
  onView: (id: number) => void;
  onEdit?: (id: number) => void;
  onPublish?: (id: number) => void;
  onClose?: (id: number) => void;
  onDelete?: (id: number) => void;
  onStartExam?: (id: number) => void;
}

export default function ExamCard({
  exam,
  onView,
  onEdit,
  onPublish,
  onClose,
  onDelete,
  onStartExam,
}: ExamCardProps) {
  const actions = getActions(exam.status);

  return (
    <div className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="mb-3 flex items-start justify-between">
        <h3 className="min-w-0 flex-1 truncate text-base font-semibold text-gray-900">
          {exam.title}
        </h3>
        <StatusBadge status={exam.status} className="ml-2 shrink-0" />
      </div>

      <div className="mb-4 flex flex-wrap gap-3 text-sm text-gray-500">
        <span className="flex items-center gap-1">
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
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          {exam.question_count} 题
        </span>
        <span className="flex items-center gap-1">
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
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          {exam.duration_minutes} 分钟
        </span>
        <span className="flex items-center gap-1">
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
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          {exam.total_score} 分
        </span>
      </div>

      {exam.created_at && (
        <p className="mb-4 text-xs text-gray-400">
          创建于 {new Date(exam.created_at).toLocaleString("zh-CN")}
        </p>
      )}

      <div className="flex flex-wrap gap-2 border-t border-gray-100 pt-3">
        {actions.includes("view") && (
          <button
            type="button"
            onClick={() => onView(exam.id)}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-100"
          >
            查看
          </button>
        )}
        {actions.includes("edit") && onEdit && (
          <button
            type="button"
            onClick={() => onEdit(exam.id)}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-100"
          >
            编辑
          </button>
        )}
        {actions.includes("publish") && onPublish && (
          <button
            type="button"
            onClick={() => onPublish(exam.id)}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-emerald-600 transition-colors hover:bg-emerald-50"
          >
            发布
          </button>
        )}
        {actions.includes("startExam") && onStartExam && (
          <button
            type="button"
            onClick={() => onStartExam(exam.id)}
            className="rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-primary-700"
          >
            开始考试
          </button>
        )}
        {actions.includes("close") && onClose && (
          <button
            type="button"
            onClick={() => onClose(exam.id)}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-amber-600 transition-colors hover:bg-amber-50"
          >
            关闭
          </button>
        )}
        {actions.includes("delete") && onDelete && (
          <button
            type="button"
            onClick={() => onDelete(exam.id)}
            className="rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 transition-colors hover:bg-red-50"
          >
            删除
          </button>
        )}
      </div>
    </div>
  );
}

function getActions(status: ExamStatus): string[] {
  switch (status) {
    case "draft":
      return ["view", "edit", "publish", "delete"];
    case "open":
      return ["view", "startExam", "close"];
    case "closed":
      return ["view", "delete"];
    default:
      return ["view"];
  }
}
