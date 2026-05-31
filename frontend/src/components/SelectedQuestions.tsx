"use client";

import { useMemo } from "react";
import type { SelectedQuestion, QuestionType } from "@/types/question";

const TYPE_LABELS: Record<QuestionType, string> = {
  single: "单选题",
  multi: "多选题",
  judge: "判断题",
  fill: "填空题",
  essay: "简答题",
};

const TYPE_BADGE_COLORS: Record<QuestionType, string> = {
  single: "bg-blue-100 text-blue-700",
  multi: "bg-purple-100 text-purple-700",
  judge: "bg-emerald-100 text-emerald-700",
  fill: "bg-amber-100 text-amber-700",
  essay: "bg-gray-100 text-gray-700",
};

interface SelectedQuestionsProps {
  questions: SelectedQuestion[];
  onReorder: (fromIndex: number, toIndex: number) => void;
  onScoreChange: (id: number, score: number) => void;
  onRemove: (id: number) => void;
}

export default function SelectedQuestions({
  questions,
  onReorder,
  onScoreChange,
  onRemove,
}: SelectedQuestionsProps) {
  const totalScore = useMemo(
    () => questions.reduce((sum, q) => sum + q.score, 0),
    [questions]
  );

  const handleMoveUp = (index: number) => {
    if (index > 0) {
      onReorder(index, index - 1);
    }
  };

  const handleMoveDown = (index: number) => {
    if (index < questions.length - 1) {
      onReorder(index, index + 1);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-lg border border-gray-200 bg-white">
      <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-800">
          已选题目
        </h3>
        <div className="text-sm text-gray-500">
          <span className="font-semibold text-primary-600">
            {questions.length}
          </span>{" "}
          题 · 共{" "}
          <span className="font-semibold text-primary-600">
            {totalScore}
          </span>{" "}
          分
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {questions.length === 0 && (
          <div className="px-4 py-12 text-center text-sm text-gray-400">
            请从左侧选择题目
          </div>
        )}

        {questions.map((q, index) => (
          <div
            key={q.id}
            className="flex items-center gap-2 border-b border-gray-50 px-3 py-2.5 last:border-b-0"
          >
            <div className="flex flex-col gap-0.5">
              <button
                type="button"
                onClick={() => handleMoveUp(index)}
                disabled={index === 0}
                className="rounded p-0.5 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 disabled:cursor-not-allowed disabled:opacity-30"
                title="上移"
              >
                <svg
                  className="h-3.5 w-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 15l7-7 7 7"
                  />
                </svg>
              </button>
              <button
                type="button"
                onClick={() => handleMoveDown(index)}
                disabled={index === questions.length - 1}
                className="rounded p-0.5 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 disabled:cursor-not-allowed disabled:opacity-30"
                title="下移"
              >
                <svg
                  className="h-3.5 w-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
            </div>

            <span className="w-5 shrink-0 text-center text-xs font-medium text-gray-400">
              {index + 1}
            </span>

            <span
              className={`shrink-0 rounded-md px-1.5 py-0.5 text-xs font-medium ${TYPE_BADGE_COLORS[q.type]}`}
            >
              {TYPE_LABELS[q.type]}
            </span>

            <span className="min-w-0 flex-1 truncate text-sm text-gray-700">
              {q.content.length > 40
                ? q.content.slice(0, 40) + "..."
                : q.content}
            </span>

            <div className="flex items-center gap-1">
              <input
                type="number"
                value={q.score}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  if (!isNaN(val) && val > 0) {
                    onScoreChange(q.id, val);
                  }
                }}
                className="w-14 rounded border border-gray-200 px-1.5 py-0.5 text-center text-xs text-gray-700 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500/20"
                min={1}
              />
              <span className="text-xs text-gray-400">分</span>
            </div>

            <button
              type="button"
              onClick={() => onRemove(q.id)}
              className="rounded p-1 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500"
              title="移除"
            >
              <svg
                className="h-3.5 w-3.5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
