"use client";

interface QuestionNavProps {
  total: number;
  currentIndex: number;
  answeredIds: Set<number>;
  onNavigate: (index: number) => void;
  onSubmit: () => void;
  submitting: boolean;
}

export default function QuestionNav({
  total,
  currentIndex,
  answeredIds,
  onNavigate,
  onSubmit,
  submitting,
}: QuestionNavProps) {
  const answeredCount = answeredIds.size;
  const progress = total > 0 ? Math.round((answeredCount / total) * 100) : 0;

  return (
    <div className="flex h-full flex-col rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
      {/* 进度 */}
      <div className="mb-4">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-gray-600">答题进度</span>
          <span className="font-medium text-gray-900">
            {answeredCount} / {total}
          </span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-gray-100">
          <div
            className="h-full rounded-full bg-primary-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 题号网格 */}
      <div className="mb-4 flex-1 overflow-y-auto">
        <div className="grid grid-cols-5 gap-2">
          {Array.from({ length: total }, (_, i) => {
            const isCurrent = i === currentIndex;
            const isAnswered = answeredIds.has(i);

            return (
              <button
                key={i}
                type="button"
                onClick={() => onNavigate(i)}
                className={`flex h-10 w-10 items-center justify-center rounded-lg text-sm font-medium transition-colors ${
                  isCurrent
                    ? "border-2 border-primary-500 bg-primary-50 text-primary-700"
                    : isAnswered
                      ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
                      : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                }`}
              >
                {i + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* 图例 */}
      <div className="mb-4 flex flex-wrap gap-3 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 rounded border-2 border-primary-500 bg-primary-50" />
          <span>当前</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 rounded bg-emerald-100" />
          <span>已答</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="h-3 w-3 rounded bg-gray-50" />
          <span>未答</span>
        </div>
      </div>

      {/* 提交按钮 */}
      <button
        type="button"
        onClick={onSubmit}
        disabled={submitting}
        className="w-full rounded-lg bg-primary-600 px-4 py-3 text-sm font-medium text-white shadow-sm transition-colors hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500/20 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {submitting ? "提交中..." : "提交考试"}
      </button>
    </div>
  );
}
