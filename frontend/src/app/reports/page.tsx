"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { reportApi } from "@/lib/api";
import { useAuthStore } from "@/hooks/useAuth";
import type { ReportOverview, TrendData } from "@/lib/api";
import TrendChart from "@/components/TrendChart";

type TimeRange = 7 | 30 | 0;

export default function ReportsPage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [overview, setOverview] = useState<ReportOverview | null>(null);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [timeRange, setTimeRange] = useState<TimeRange>(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [overviewRes, trendRes] = await Promise.all([
          reportApi.getOverview(),
          reportApi.getTrend(timeRange),
        ]);

        setOverview(overviewRes.data);
        setTrendData(trendRes.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "加载失败");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-sm">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
            <svg
              className="h-8 w-8 text-red-600"
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
          <h1 className="mb-2 text-xl font-bold text-gray-900">加载失败</h1>
          <p className="mb-6 text-gray-500">{error}</p>
          <button
            type="button"
            onClick={() => router.push("/exams")}
            className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            返回考试列表
          </button>
        </div>
      </div>
    );
  }

  const stats = [
    {
      label: "考试次数",
      value: overview?.total_attempts ?? 0,
      suffix: "次",
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      label: "平均分",
      value: overview?.average_score ?? 0,
      suffix: "分",
      color: "text-emerald-600",
      bg: "bg-emerald-50",
    },
    {
      label: "最高分",
      value: overview?.max_score ?? 0,
      suffix: "分",
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
    {
      label: "通过率",
      value: overview?.pass_rate ?? 0,
      suffix: "%",
      color: "text-amber-600",
      bg: "bg-amber-50",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-6">
            <h1 className="text-lg font-semibold text-gray-900">学习统计</h1>
            <nav className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => router.push("/exams")}
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                考试列表
              </button>
              <button
                type="button"
                onClick={() => router.push("/upload")}
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                上传试卷
              </button>
              <button
                type="button"
                onClick={() => router.push("/questions")}
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                题库
              </button>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user?.username || "未登录"}
            </span>
            <button
              type="button"
              onClick={() => {
                logout();
                router.push("/auth");
              }}
              className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
            >
              退出登录
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-4xl px-6 py-8">
        {/* 标题 */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">学习统计</h1>
          <p className="mt-1 text-sm text-gray-500">
            查看您的考试成绩和学习趋势
          </p>
        </div>

        {/* 统计卡片 */}
        <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className={`rounded-2xl ${stat.bg} p-5`}
            >
              <div className="text-sm text-gray-600">{stat.label}</div>
              <div className={`mt-2 text-3xl font-bold ${stat.color}`}>
                {typeof stat.value === "number"
                  ? stat.value % 1 === 0
                    ? stat.value
                    : stat.value.toFixed(1)
                  : stat.value}
                <span className="ml-1 text-sm font-normal">{stat.suffix}</span>
              </div>
            </div>
          ))}
        </div>

        {/* 趋势图 */}
        <div className="rounded-2xl bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">成绩趋势</h2>
            <div className="flex gap-2">
              {([7, 30, 0] as TimeRange[]).map((range) => (
                <button
                  key={range}
                  type="button"
                  onClick={() => setTimeRange(range)}
                  className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                    timeRange === range
                      ? "bg-primary-100 text-primary-700"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  {range === 0 ? "全部" : `${range}天`}
                </button>
              ))}
            </div>
          </div>
          <TrendChart data={trendData} />
        </div>

        {/* 空状态提示 */}
        {overview?.total_attempts === 0 && (
          <div className="mt-8 rounded-2xl bg-white p-8 text-center shadow-sm">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
              <svg
                className="h-8 w-8 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="mb-2 text-lg font-medium text-gray-900">
              暂无考试记录
            </h3>
            <p className="mb-6 text-gray-500">
              完成考试后，这里将显示您的学习统计数据
            </p>
            <button
              type="button"
              onClick={() => router.push("/exams")}
              className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
            >
              开始考试
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
