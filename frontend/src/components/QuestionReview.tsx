"use client";

import { useState } from "react";
import type { QuestionResult } from "@/types/exam";

interface QuestionReviewProps {
  questions: QuestionResult[];
}

const TYPE_LABELS: Record<string, string> = {
  single: "单选",
  multi: "多选",
  judge: "判断",
  fill: "填空",
  essay: "简答",
};

const TYPE_COLORS: Record<string, { bg: string; text: string }> = {
  single: { bg: "bg-blue-100", text: "text-blue-700" },
  multi: { bg: "bg-purple-100", text: "text-purple-700" },
  judge: { bg: "bg-emerald-100", text: "text-emerald-700" },
  fill: { bg: "bg-amber-100", text: "text-amber-700" },
  essay: { bg: "bg-gray-100", text: "text-gray-700" },
};

export default function QuestionReview({ questions }: QuestionReviewProps) {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  if (questions.length === 0) {
    return (
      <div className="rounded-2xl bg-white p-6 shadow-sm">
        <p className="text-center text-gray-500">暂无题目数据</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {questions.map((q, index) => {
        const colors = TYPE_COLORS[q.type] || TYPE_COLORS.essay;
        const label = TYPE_LABELS[q.type] || q.type;
        const isExpanded = expandedId === q.id;
        const isPending = q.earned_score === null && q.is_correct === null;
        const isCorrect = q.is_correct === true;
        const isWrong = q.is_correct === false;

        return (
          <div
            key={q.id}
            className="overflow-hidden rounded-2xl bg-white shadow-sm"
          >
            {/* 题目头部 */}
            <button
              type="button"
              className="flex w-full items-center justify-between p-4 text-left transition-colors hover:bg-gray-50"
              onClick={() => setExpandedId(isExpanded ? null : q.id)}
            >
              <div className="flex items-center gap-3">
                {/* 题号 */}
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-sm font-medium text-gray-700">
                  {index + 1}
                </span>

                {/* 题型标签 */}
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${colors.bg} ${colors.text}`}
                >
                  {label}
                </span>

                {/* 题目内容（截断） */}
                <span className="text-sm text-gray-700 line-clamp-1">
                  {q.content}
                </span>
              </div>

              <div className="flex items-center gap-3">
                {/* 得分 */}
                <span
                  className={`text-sm font-medium ${
                    isPending
                      ? "text-amber-600"
                      : isCorrect
                        ? "text-emerald-600"
                        : "text-red-600"
                  }`}
                >
                  {isPending ? "待评分" : `${q.earned_score}/${q.score}`}
                </span>

                {/* 对错标记 */}
                {!isPending && (
                  <span
                    className={`flex h-6 w-6 items-center justify-center rounded-full ${
                      isCorrect ? "bg-emerald-100" : "bg-red-100"
                    }`}
                  >
                    {isCorrect ? (
                      <svg
                        className="h-4 w-4 text-emerald-600"
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
                    ) : (
                      <svg
                        className="h-4 w-4 text-red-600"
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
                    )}
                  </span>
                )}

                {/* 展开/收起图标 */}
                <svg
                  className={`h-5 w-5 text-gray-400 transition-transform ${
                    isExpanded ? "rotate-180" : ""
                  }`}
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
              </div>
            </button>

            {/* 展开内容 */}
            {isExpanded && (
              <div className="border-t border-gray-100 p-4">
                {/* 题目内容 */}
                <div className="mb-4">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">
                    {q.content}
                  </p>
                </div>

                {/* 选项（如果有） */}
                {q.options && q.options.length > 0 && (
                  <div className="mb-4 space-y-2">
                    {q.options.map((opt) => {
                      const isUserSelected =
                        q.user_answer?.includes(opt.label) ?? false;
                      const isCorrectOption =
                        q.correct_answer?.includes(opt.label) ?? false;

                      return (
                        <div
                          key={opt.id}
                          className={`flex items-start gap-2 rounded-lg p-2 text-sm ${
                            isCorrectOption
                              ? "bg-emerald-50 text-emerald-800"
                              : isUserSelected && !isCorrectOption
                                ? "bg-red-50 text-red-800"
                                : "bg-gray-50 text-gray-700"
                          }`}
                        >
                          <span className="font-medium">{opt.label}.</span>
                          <span>{opt.content}</span>
                          {isCorrectOption && (
                            <span className="ml-auto text-xs font-medium text-emerald-600">
                              正确答案
                            </span>
                          )}
                          {isUserSelected && !isCorrectOption && (
                            <span className="ml-auto text-xs font-medium text-red-600">
                              你的选择
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* 用户答案和正确答案 */}
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-lg bg-gray-50 p-3">
                    <div className="mb-1 text-xs font-medium text-gray-500">
                      你的答案
                    </div>
                    <div className="text-sm text-gray-900">
                      {q.user_answer || (
                        <span className="text-gray-400">未作答</span>
                      )}
                    </div>
                  </div>
                  <div className="rounded-lg bg-emerald-50 p-3">
                    <div className="mb-1 text-xs font-medium text-emerald-600">
                      正确答案
                    </div>
                    <div className="text-sm text-emerald-900">
                      {q.correct_answer}
                    </div>
                  </div>
                </div>

                {/* 解析（如果有） */}
                {q.explanation && (
                  <div className="mt-4 rounded-lg bg-blue-50 p-3">
                    <div className="mb-1 text-xs font-medium text-blue-600">
                      解析
                    </div>
                    <div className="text-sm text-blue-900 whitespace-pre-wrap">
                      {q.explanation}
                    </div>
                  </div>
                )}

                {/* 简答题待评分提示 */}
                {q.type === "essay" && isPending && (
                  <div className="mt-4 rounded-lg bg-amber-50 p-3 text-center">
                    <span className="text-sm text-amber-700">
                      简答题需要人工评分，请等待教师批阅
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
