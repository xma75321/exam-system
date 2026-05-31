"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type SaveStatus = "idle" | "saving" | "saved" | "error";

interface UseAutoSaveOptions {
  /** 保存函数 */
  saveFn: () => Promise<void>;
  /** 自动保存间隔（毫秒），默认 30000（30 秒） */
  interval?: number;
  /** 最大重试次数 */
  maxRetries?: number;
}

interface UseAutoSaveReturn {
  /** 当前保存状态 */
  status: SaveStatus;
  /** 标记答案有变更 */
  markDirty: () => void;
  /** 立即保存 */
  saveNow: () => Promise<void>;
  /** 启动自动保存 */
  startAutoSave: () => void;
  /** 停止自动保存 */
  stopAutoSave: () => void;
  /** 手动重试 */
  retry: () => Promise<void>;
}

export function useAutoSave({
  saveFn,
  interval = 30000,
  maxRetries = 3,
}: UseAutoSaveOptions): UseAutoSaveReturn {
  const [status, setStatus] = useState<SaveStatus>("idle");

  const isDirtyRef = useRef(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryCountRef = useRef(0);
  const isActiveRef = useRef(false);
  const saveFnRef = useRef(saveFn);

  // 更新 saveFn 引用
  useEffect(() => {
    saveFnRef.current = saveFn;
  }, [saveFn]);

  // 清理定时器
  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  // 执行保存
  const doSave = useCallback(async () => {
    if (!isDirtyRef.current) return;

    setStatus("saving");
    try {
      await saveFnRef.current();
      isDirtyRef.current = false;
      retryCountRef.current = 0;
      setStatus("saved");

      // 3 秒后恢复 idle
      setTimeout(() => {
        setStatus((prev) => (prev === "saved" ? "idle" : prev));
      }, 3000);
    } catch {
      retryCountRef.current += 1;
      if (retryCountRef.current < maxRetries) {
        setStatus("error");
        // 递增重试间隔
        const retryDelay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000);
        timerRef.current = setTimeout(doSave, retryDelay);
      } else {
        setStatus("error");
      }
    }
  }, [maxRetries]);

  // 标记有变更
  const markDirty = useCallback(() => {
    isDirtyRef.current = true;
    clearTimer();

    // 启动新的自动保存计时器
    if (isActiveRef.current) {
      timerRef.current = setTimeout(doSave, interval);
    }
  }, [clearTimer, doSave, interval]);

  // 立即保存
  const saveNow = useCallback(async () => {
    clearTimer();
    await doSave();
  }, [clearTimer, doSave]);

  // 启动自动保存
  const startAutoSave = useCallback(() => {
    isActiveRef.current = true;
    if (isDirtyRef.current) {
      timerRef.current = setTimeout(doSave, interval);
    }
  }, [doSave, interval]);

  // 停止自动保存
  const stopAutoSave = useCallback(() => {
    isActiveRef.current = false;
    clearTimer();
  }, [clearTimer]);

  // 手动重试
  const retry = useCallback(async () => {
    retryCountRef.current = 0;
    await doSave();
  }, [doSave]);

  // 页面关闭前保存
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (isDirtyRef.current) {
        // 使用 sendBeacon 或同步 XHR 保存
        // 这里简化处理，实际可能需要更复杂的逻辑
        navigator.sendBeacon?.("/api/attempts/save", JSON.stringify({}));
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, []);

  // 组件卸载时清理
  useEffect(() => {
    return () => {
      clearTimer();
    };
  }, [clearTimer]);

  return {
    status,
    markDirty,
    saveNow,
    startAutoSave,
    stopAutoSave,
    retry,
  };
}
