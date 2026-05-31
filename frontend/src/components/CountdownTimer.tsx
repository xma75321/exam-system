"use client";

interface CountdownTimerProps {
  formattedTime: string;
  isWarning: boolean;
  isExpired: boolean;
}

export default function CountdownTimer({
  formattedTime,
  isWarning,
  isExpired,
}: CountdownTimerProps) {
  return (
    <div className="sticky top-0 z-10 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
      <div className="mb-1 text-xs font-medium text-gray-500">剩余时间</div>
      <div
        className={`font-mono text-2xl font-bold tracking-wider ${
          isExpired
            ? "text-gray-400"
            : isWarning
              ? "animate-pulse text-red-600"
              : "text-gray-900"
        }`}
      >
        {isExpired ? "00:00" : formattedTime}
      </div>
      {isWarning && !isExpired && (
        <div className="mt-2 text-xs text-red-500">即将到期，请尽快完成</div>
      )}
      {isExpired && (
        <div className="mt-2 text-xs text-gray-400">时间已到</div>
      )}
    </div>
  );
}
