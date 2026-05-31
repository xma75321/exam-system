"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class GlobalErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // 在开发环境记录错误详情
    if (process.env.NODE_ENV === "development") {
      console.error("ErrorBoundary caught an error:", error, errorInfo);
    }
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-sm">
            {/* 错误图标 */}
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-100">
              <svg
                className="h-10 w-10 text-red-600"
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
            </div>

            {/* 标题 */}
            <h1 className="mb-2 text-2xl font-bold text-gray-900">
              出错了
            </h1>
            <p className="mb-6 text-gray-500">
              页面发生了意外错误，请尝试刷新页面
            </p>

            {/* 开发环境显示错误详情 */}
            {process.env.NODE_ENV === "development" && this.state.error && (
              <div className="mb-6 rounded-lg bg-gray-50 p-4 text-left">
                <p className="mb-2 text-xs font-medium text-gray-500">
                  错误详情（仅开发环境显示）
                </p>
                <p className="break-all text-xs text-red-600">
                  {this.state.error.message}
                </p>
                {this.state.error.stack && (
                  <pre className="mt-2 max-h-32 overflow-auto text-xs text-gray-600">
                    {this.state.error.stack}
                  </pre>
                )}
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex flex-col gap-3">
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="w-full rounded-lg bg-primary-600 px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-primary-700"
              >
                刷新页面
              </button>
              <button
                type="button"
                onClick={() => {
                  this.handleReset();
                  window.location.href = "/";
                }}
                className="w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
              >
                返回首页
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
