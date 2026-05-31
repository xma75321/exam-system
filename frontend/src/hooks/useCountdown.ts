"use client";

import { useEffect, useRef, useState, useCallback } from "react";

interface UseCountdownOptions {
  /** 结束时间（ISO 字符串或 Date） */
  endTime: string | Date;
  /** 警告阈值（秒），默认 300（5 分钟） */
  warningThreshold?: number;
  /** 倒计时结束回调 */
  onExpire?: () => void;
  /** 进入警告状态回调 */
  onWarning?: () => void;
}

interface UseCountdownReturn {
  /** 剩余秒数 */
  remainingSeconds: number;
  /** 是否处于警告状态 */
  isWarning: boolean;
  /** 是否已过期 */
  isExpired: boolean;
  /** 格式化的时间字符串 */
  formattedTime: string;
}

export function useCountdown({
  endTime,
  warningThreshold = 300,
  onExpire,
  onWarning,
}: UseCountdownOptions): UseCountdownReturn {
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [isWarning, setIsWarning] = useState(false);
  const [isExpired, setIsExpired] = useState(false);

  const onExpireRef = useRef(onExpire);
  const onWarningRef = useRef(onWarning);
  const warningTriggeredRef = useRef(false);

  // 更新回调引用
  useEffect(() => {
    onExpireRef.current = onExpire;
    onWarningRef.current = onWarning;
  }, [onExpire, onWarning]);

  // 计算剩余时间
  useEffect(() => {
    const end = new Date(endTime).getTime();

    const updateRemaining = () => {
      const now = Date.now();
      const remaining = Math.max(0, Math.floor((end - now) / 1000));

      setRemainingSeconds(remaining);
      setIsWarning(remaining > 0 && remaining <= warningThreshold);
      setIsExpired(remaining <= 0);

      // 触发警告回调
      if (remaining > 0 && remaining <= warningThreshold && !warningTriggeredRef.current) {
        warningTriggeredRef.current = true;
        onWarningRef.current?.();
      }

      // 触发过期回调
      if (remaining <= 0) {
        onExpireRef.current?.();
      }
    };

    // 立即更新一次
    updateRemaining();

    // 每秒更新
    const interval = setInterval(updateRemaining, 1000);

    return () => clearInterval(interval);
  }, [endTime, warningThreshold]);

  // 格式化时间
  const formattedTime = formatTime(remainingSeconds);

  return {
    remainingSeconds,
    isWarning,
    isExpired,
    formattedTime,
  };
}

function formatTime(seconds: number): string {
  if (seconds <= 0) return "00:00";

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`;
  }
  return `${pad(minutes)}:${pad(secs)}`;
}

function pad(n: number): string {
  return n.toString().padStart(2, "0");
}
