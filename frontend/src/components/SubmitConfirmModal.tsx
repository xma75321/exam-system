"use client";

interface SubmitConfirmModalProps {
  open: boolean;
  totalQuestions: number;
  answeredCount: number;
  submitting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function SubmitConfirmModal({
  open,
  totalQuestions,
  answeredCount,
  submitting,
  onConfirm,
  onCancel,
}: SubmitConfirmModalProps) {
  if (!open) return null;

  const unansweredCount = totalQuestions - answeredCount;
  const hasUnanswered = unansweredCount > 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          确认提交考试
        </h3>

        {/* 答题统计 */}
        <div className="mb-6 rounded-lg bg-gray-50 p-4">
          <div className="mb-3 text-sm font-medium text-gray-700">答题统计</div>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{totalQuestions}</div>
              <div className="text-xs text-gray-500">总题数</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-emerald-600">{answeredCount}</div>
              <div className="text-xs text-gray-500">已答</div>
            </div>
            <div>
              <div className={`text-2xl font-bold ${hasUnanswered ? "text-amber-600" : "text-gray-400"}`}>
                {unansweredCount}
              </div>
              <div className="text-xs text-gray-500">未答</div>
            </div>
          </div>
        </div>

        {/* 警告信息 */}
        {hasUnanswered && (
          <div className="mb-6 flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3">
            <svg
              className="mt-0.5 h-5 w-5 shrink-0 text-amber-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
            <div className="text-sm text-amber-700">
              您还有 <span className="font-semibold">{unansweredCount}</span> 道题目未作答，
              未答题目将不得分。确定要提交吗？
            </div>
          </div>
        )}

        {!hasUnanswered && (
          <p className="mb-6 text-sm text-gray-500">
            提交后将无法修改答案，请确认无误后再提交。
          </p>
        )}

        {/* 按钮 */}
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={submitting}
            className="rounded-lg px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            继续答题
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={submitting}
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {submitting ? (
              <span className="flex items-center gap-2">
                <svg
                  className="h-4 w-4 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                提交中...
              </span>
            ) : (
              "确认提交"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
