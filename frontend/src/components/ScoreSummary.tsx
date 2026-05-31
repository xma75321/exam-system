"use client";

interface ScoreSummaryProps {
  totalScore: number | null;
  passScore: number;
  totalQuestions: number;
  correctCount: number;
  pendingCount: number;
  durationMinutes: number;
  submittedAt?: string | null;
  startedAt: string;
  isPassed: boolean | null;
}

export default function ScoreSummary({
  totalScore,
  passScore,
  totalQuestions,
  correctCount,
  pendingCount,
  durationMinutes,
  submittedAt,
  startedAt,
  isPassed,
}: ScoreSummaryProps) {
  // 计算用时
  const calculateDuration = () => {
    if (!submittedAt) return durationMinutes;
    const start = new Date(startedAt);
    const end = new Date(submittedAt);
    const diffMs = end.getTime() - start.getTime();
    return Math.round(diffMs / 60000);
  };

  const actualDuration = calculateDuration();
  const scoreDisplay = totalScore !== null ? totalScore.toFixed(1) : "--";
  const accuracy = totalQuestions > 0 ? `${correctCount}/${totalQuestions}` : "--";

  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      {/* 分数显示 */}
      <div className="mb-6 text-center">
        <div className="mb-2 flex items-baseline justify-center gap-1">
          <span className="text-5xl font-bold text-gray-900">{scoreDisplay}</span>
          <span className="text-xl text-gray-500">分</span>
        </div>

        {/* 通过/未通过标签 */}
        {isPassed !== null && (
          <span
            className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${
              isPassed
                ? "bg-emerald-100 text-emerald-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {isPassed ? "通过" : "未通过"}
          </span>
        )}

        {pendingCount > 0 && (
          <span className="ml-2 inline-flex items-center rounded-full bg-amber-100 px-3 py-1 text-sm font-medium text-amber-700">
            {pendingCount} 题待评分
          </span>
        )}
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-2 gap-4 rounded-lg bg-gray-50 p-4 sm:grid-cols-4">
        <div className="text-center">
          <div className="text-2xl font-semibold text-gray-900">{totalScore !== null ? totalScore.toFixed(0) : "--"}</div>
          <div className="text-xs text-gray-500">得分</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-semibold text-gray-900">{passScore.toFixed(0)}</div>
          <div className="text-xs text-gray-500">及格线</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-semibold text-gray-900">{accuracy}</div>
          <div className="text-xs text-gray-500">正确率</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-semibold text-gray-900">{actualDuration} 分钟</div>
          <div className="text-xs text-gray-500">用时</div>
        </div>
      </div>
    </div>
  );
}
