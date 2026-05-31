"use client";

import type { QuestionType, Option } from "@/types/question";
import AnswerInput from "./AnswerInput";

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

interface QuestionInExam {
  id: number;
  type: QuestionType;
  content: string;
  score: number;
  sort_order: number;
  options?: Option[];
}

interface QuestionDisplayProps {
  question: QuestionInExam;
  currentIndex: number;
  total: number;
  answer: string;
  onAnswerChange: (answer: string) => void;
}

export default function QuestionDisplay({
  question,
  currentIndex,
  total,
  answer,
  onAnswerChange,
}: QuestionDisplayProps) {
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
      {/* 题目头部 */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-lg font-semibold text-gray-900">
            第 {currentIndex + 1} / {total} 题
          </span>
          <span
            className={`rounded-md px-2 py-0.5 text-xs font-medium ${TYPE_BADGE_COLORS[question.type]}`}
          >
            {TYPE_LABELS[question.type]}
          </span>
        </div>
        <span className="text-sm text-gray-500">{question.score} 分</span>
      </div>

      {/* 题目内容 */}
      <div className="mb-6 text-gray-800 leading-relaxed">{question.content}</div>

      {/* 答题区 */}
      <AnswerInput
        type={question.type}
        options={question.options}
        value={answer}
        onChange={onAnswerChange}
      />
    </div>
  );
}
