"use client";

import type { SaveStatus } from "@/hooks/useAutoSave";

interface SaveIndicatorProps {
  status: SaveStatus;
  onRetry?: () => void;
}

export default function SaveIndicator({ status, onRetry }: SaveIndicatorProps) {
  if (status === "idle") return null;

  return (
    <div className="flex items-center gap-2 text-sm">
      {status === "saving" && (
        <>
          <svg
            className="h-4 w-4 animate-spin text-gray-400"
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
          <span className="text-gray-400">保存中...</span>
        </>
      )}

      {status === "saved" && (
        <>
          <svg
            className="h-4 w-4 text-emerald-500"
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
          <span className="text-emerald-600">已保存</span>
        </>
      )}

      {status === "error" && (
        <button
          type="button"
          onClick={onRetry}
          className="flex items-center gap-1 text-red-500 hover:text-red-600"
        >
          <svg
            className="h-4 w-4"
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
          <span>保存失败，点击重试</span>
        </button>
      )}
    </div>
  );
}
