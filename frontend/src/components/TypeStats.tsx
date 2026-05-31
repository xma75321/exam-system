"use client";

import type { TypeStat } from "@/types/exam";

interface TypeStatsProps {
  typeStats: TypeStat[];
}

const TYPE_LABELS: Record<string, string> = {
  single: "单选题",
  multi: "多选题",
  judge: "判断题",
  fill: "填空题",
  essay: "简答题",
};

const TYPE_COLORS: Record<string, { bg: string; text: string }> = {
  single: { bg: "bg-blue-100", text: "text-blue-700" },
  multi: { bg: "bg-purple-100", text: "text-purple-700" },
  judge: { bg: "bg-emerald-100", text: "text-emerald-700" },
  fill: { bg: "bg-amber-100", text: "text-amber-700" },
  essay: { bg: "bg-gray-100", text: "text-gray-700" },
};

export default function TypeStats({ typeStats }: TypeStatsProps) {
  if (typeStats.length === 0) {
    return null;
  }

  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-gray-900">题型统计</h2>
      <div className="space-y-3">
        {typeStats.map((stat) => {
          const colors = TYPE_COLORS[stat.type] || TYPE_COLORS.essay;
          const label = TYPE_LABELS[stat.type] || stat.type;
          const isPending = stat.pending > 0;

          return (
            <div
              key={stat.type}
              className="flex items-center justify-between rounded-lg border border-gray-100 p-3"
            >
              <div className="flex items-center gap-3">
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${colors.bg} ${colors.text}`}
                >
                  {label}
                </span>
                <span className="text-sm text-gray-500">
                  {stat.total} 题
                </span>
              </div>
              <div className="text-sm font-medium">
                {isPending ? (
                  <span className="text-amber-600">
                    {stat.correct}/{stat.total} 正确，{stat.pending} 待评分
                  </span>
                ) : (
                  <span
                    className={
                      stat.correct === stat.total
                        ? "text-emerald-600"
                        : "text-gray-900"
                    }
                  >
                    {stat.correct}/{stat.total} 正确
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
