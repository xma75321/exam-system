"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastContextValue {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

let nextId = 0;

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return ctx;
}

const TYPE_STYLES: Record<ToastType, string> = {
  success: "bg-emerald-500 text-white",
  error: "bg-red-500 text-white",
  info: "bg-primary-600 text-white",
};

const TYPE_ICONS: Record<ToastType, string> = {
  success: "\u2713",
  error: "\u2717",
  info: "\u2139",
};

function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: number) => void }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onRemove(toast.id);
    }, 5000); // 延长到 5 秒
    return () => clearTimeout(timer);
  }, [toast.id, onRemove]);

  return (
    <div
      className={`${TYPE_STYLES[toast.type]} flex items-center gap-2 rounded-lg px-4 py-3 text-sm font-medium shadow-lg transition-all duration-300 animate-slide-in`}
    >
      <span className="text-base">{TYPE_ICONS[toast.type]}</span>
      <span>{toast.message}</span>
    </div>
  );
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const removeToast = useCallback((id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((message: string, type: ToastType = "info") => {
    const id = nextId++;
    setToasts((prev) => [...prev, { id, message, type }]);
  }, []);

  const contextValue = useRef({ showToast });
  contextValue.current = { showToast };

  return (
    <ToastContext.Provider value={contextValue.current}>
      {children}
      {mounted &&
        createPortal(
          <div className="fixed right-4 top-4 z-50 flex flex-col gap-2">
            {toasts.map((toast) => (
              <ToastItem key={toast.id} toast={toast} onRemove={removeToast} />
            ))}
          </div>,
          document.body
        )}
    </ToastContext.Provider>
  );
}