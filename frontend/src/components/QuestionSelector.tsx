"use client";

import { useEffect, useState } from "react";
import { questionApi } from "@/lib/api";
import type { Question, QuestionType } from "@/types/question";

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

const FILTER_OPTIONS: { value: QuestionType | "all"; label: string }[] = [
  { value: "all", label: "全部" },
  { value: "single", label: "单选题" },
  { value: "multi", label: "多选题" },
  { value: "judge", label: "判断题" },
  { value: "fill", label: "填空题" },
  { value: "essay", label: "简答题" },
];

interface QuestionSelectorProps {
  selectedIds: number[];
  onSelectionChange: (ids: number[]) => void;
}

export default function QuestionSelector({
  selectedIds,
  onSelectionChange,
}: QuestionSelectorProps) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<QuestionType | "all">("all");

  useEffect(() => {
    async function loadQuestions() {
      try {
        setLoading(true);
        setError(null);
        const res = await questionApi.list(1, 50, filterType === "all" ? undefined : filterType);
        setQuestions(res.data.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载题目失败");
      } finally {
        setLoading(false);
      }
    }
    loadQuestions();
  }, [filterType]);

  const filteredQuestions = questions;
  const selectedSet = new Set(selectedIds);

  const allFilteredSelected =
    filteredQuestions.length > 0 &&
    filteredQuestions.every((q) => selectedSet.has(q.id));

  const handleToggleAll = () => {
    if (allFilteredSelected) {
      const filteredIds = new Set(filteredQuestions.map((q) => q.id));
      const newIds = selectedIds.filter((id) => !filteredIds.has(id));
      onSelectionChange(newIds);
    } else {
      const newIds = new Set(selectedIds);
      filteredQuestions.forEach((q) => newIds.add(q.id));
      onSelectionChange(Array.from(newIds));
    }
  };

  const handleToggle = (id: number) => {
    if (selectedSet.has(id)) {
      onSelectionChange(selectedIds.filter((sid) => sid !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-lg border border-gray-200 bg-white">
      <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
        <h3 className="text-sm font-semibold text-gray-800">题目列表</h3>
        <button
          type="button"
          onClick={handleToggleAll}
          className="rounded-md px-3 py-1 text-xs font-medium text-primary-600 transition-colors hover:bg-primary-50"
        >
          {allFilteredSelected ? "取消全选" : "全选"}
        </button>
      </div>

      <div className="border-b border-gray-100 px-4 py-2">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as QuestionType | "all")}
          className="rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 shadow-sm transition-colors hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
        >
          {FILTER_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading && (
          <div className="flex items-center justify-center py-12 text-sm text-gray-400">
            加载中...
          </div>
        )}

        {error && (
          <div className="px-4 py-8 text-center text-sm text-red-500">{error}</div>
        )}

        {!loading && !error && filteredQuestions.length === 0 && (
          <div className="px-4 py-8 text-center text-sm text-gray-400">
            暂无题目
          </div>
        )}

        {!loading &&
          !error &&
          filteredQuestions.map((q) => {
            const isSelected = selectedSet.has(q.id);
            return (
              <label
                key={q.id}
                className={`flex cursor-pointer items-center gap-3 border-b border-gray-50 px-4 py-3 transition-colors last:border-b-0 ${
                  isSelected
                    ? "bg-primary-50/60"
                    : "hover:bg-gray-50"
                }`}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => handleToggle(q.id)}
                  className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span
                  className={`shrink-0 rounded-md px-2 py-0.5 text-xs font-medium ${TYPE_BADGE_COLORS[q.type]}`}
                >
                  {TYPE_LABELS[q.type]}
                </span>
                <span className="min-w-0 flex-1 truncate text-sm text-gray-700">
                  {q.content.length > 100
                    ? q.content.slice(0, 100) + "..."
                    : q.content}
                </span>
                <span className="shrink-0 text-xs text-gray-400">
                  {q.score}分
                </span>
              </label>
            );
          })}
      </div>
    </div>
  );
}