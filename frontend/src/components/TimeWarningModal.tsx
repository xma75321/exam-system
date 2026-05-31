"use client";

interface TimeWarningModalProps {
  open: boolean;
  remainingSeconds: number;
  onClose: () => void;
  onSubmit: () => void;
  submitting: boolean;
}

export default function TimeWarningModal({
  open,
  remainingSeconds,
  onClose,
  onSubmit,
  submitting,
}: TimeWarningModalProps) {
  if (!open) return null;

  const isCritical = remainingSeconds <= 60;
  const minutes = Math.ceil(remainingSeconds / 60);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-center gap-3">
          <div
            className={`flex h-10 w-10 items-center justify-center rounded-full ${
              isCritical ? "bg-red-100" : "bg-amber-100"
            }`}
          >
            <svg
              className={`h-5 w-5 ${isCritical ? "text-red-600" : "text-amber-600"}`}
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
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            {isCritical ? "时间即将到期" : "时间提醒"}
          </h3>
        </div>

        <p className="mb-6 text-sm text-gray-500">
          {isCritical
            ? `仅剩 ${remainingSeconds} 秒，系统将在时间到期后自动提交。`
            : `距离考试结束还有 ${minutes} 分钟，请合理安排时间。`}
        </p>

        <div className="flex justify-end gap-3">
          {!isCritical && (
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100"
            >
              继续答题
            </button>
          )}
          <button
            type="button"
            onClick={onSubmit}
            disabled={submitting}
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {submitting ? "提交中..." : "立即提交"}
          </button>
        </div>
      </div>
    </div>
  );
}
