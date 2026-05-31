"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { QuestionType, Option } from "@/types/question";

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

export interface QuestionCardData {
  id: number;
  type: QuestionType;
  content: string;
  score: number;
  options?: Option[];
  answer?: string;
  explanation?: string;
}

interface QuestionCardProps {
  question: QuestionCardData;
  index: number;
}

export default function QuestionCard({ question, index }: QuestionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const badgeClass = TYPE_BADGE_COLORS[question.type];

  return (
    <div className="rounded-lg border border-gray-100 bg-white transition-shadow hover:shadow-sm">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-3 px-4 py-3 text-left"
      >
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-500">
          {index + 1}
        </span>
        <span className={`shrink-0 rounded-md px-2 py-0.5 text-xs font-medium ${badgeClass}`}>
          {TYPE_LABELS[question.type]}
        </span>
        <span className="min-w-0 flex-1 truncate text-sm text-gray-700">
          {question.content.length > 60
            ? question.content.slice(0, 60) + "..."
            : question.content}
        </span>
        <span className="shrink-0 text-xs text-gray-400">{question.score}分</span>
        {expanded ? (
          <ChevronUp className="h-4 w-4 shrink-0 text-gray-400" />
        ) : (
          <ChevronDown className="h-4 w-4 shrink-0 text-gray-400" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-gray-50 px-4 pb-4 pt-3">
          <div className="space-y-2">
            <div>
              <span className="text-xs font-medium text-gray-500">题目内容</span>
              <p className="mt-0.5 whitespace-pre-wrap text-sm text-gray-800">
                {question.content}
              </p>
            </div>

            {question.options && question.options.length > 0 && (
              <div>
                <span className="text-xs font-medium text-gray-500">选项</span>
                <div className="mt-1 space-y-1">
                  {question.options.map((opt) => (
                    <div
                      key={opt.label}
                      className={`flex items-start gap-2 rounded-md px-2 py-1 text-sm ${
                        opt.is_correct ? "bg-emerald-50 text-emerald-700" : "text-gray-600"
                      }`}
                    >
                      <span className="font-medium">{opt.label}.</span>
                      <span>{opt.content}</span>
                      {opt.is_correct && (
                        <span className="ml-auto text-xs font-medium">✓</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {question.answer && (
              <div>
                <span className="text-xs font-medium text-gray-500">答案</span>
                <p className="mt-0.5 text-sm text-gray-800">{question.answer}</p>
              </div>
            )}

            {question.explanation && (
              <div>
                <span className="text-xs font-medium text-gray-500">解析</span>
                <p className="mt-0.5 text-sm text-gray-600">{question.explanation}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}