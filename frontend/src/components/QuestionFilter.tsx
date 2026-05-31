"use client";

import type { QuestionType } from "@/types/question";

interface QuestionFilterProps {
  value: QuestionType | "all";
  onChange: (type: QuestionType | "all") => void;
}

const FILTER_OPTIONS: { value: QuestionType | "all"; label: string }[] = [
  { value: "all", label: "全部" },
  { value: "single", label: "单选题" },
  { value: "multi", label: "多选题" },
  { value: "judge", label: "判断题" },
  { value: "fill", label: "填空题" },
  { value: "essay", label: "简答题" },
];

export default function QuestionFilter({ value, onChange }: QuestionFilterProps) {
  return (
    <div className="flex items-center gap-3">
      <label htmlFor="question-type-filter" className="text-sm font-medium text-gray-600">
        题目类型
      </label>
      <select
        id="question-type-filter"
        value={value}
        onChange={(e) => onChange(e.target.value as QuestionType | "all")}
        className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 shadow-sm transition-colors hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
      >
        {FILTER_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}