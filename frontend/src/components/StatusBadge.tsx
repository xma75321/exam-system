"use client";

import type { ExamStatus } from "@/types/exam";

const STATUS_CONFIG: Record<
  ExamStatus,
  { label: string; className: string }
> = {
  draft: {
    label: "草稿",
    className: "bg-gray-100 text-gray-700",
  },
  open: {
    label: "开放中",
    className: "bg-emerald-100 text-emerald-700",
  },
  closed: {
    label: "已关闭",
    className: "bg-red-100 text-red-700",
  },
};

interface StatusBadgeProps {
  status: ExamStatus;
  className?: string;
}

export default function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? STATUS_CONFIG.draft;

  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ${config.className} ${className}`}
    >
      {config.label}
    </span>
  );
}
