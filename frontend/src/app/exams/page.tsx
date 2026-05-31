"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/Toast";
import { useAuthStore } from "@/hooks/useAuth";
import ExamCard from "@/components/ExamCard";
import { examApi } from "@/lib/api";
import type { ExamResponse, ExamStatus } from "@/types/exam";

const STATUS_FILTERS: { value: ExamStatus | "all"; label: string }[] = [
  { value: "all", label: "全部" },
  { value: "draft", label: "草稿" },
  { value: "open", label: "开放中" },
  { value: "closed", label: "已关闭" },
];

function ExamListPageContent() {
  const router = useRouter();
  const { showToast } = useToast();
  const { user, logout } = useAuthStore();

  const [exams, setExams] = useState<ExamResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<ExamStatus | "all">("all");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 12;

  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
  } | null>(null);

  const loadExams = useCallback(async () => {
    setLoading(true);
    try {
      const res = await examApi.list(
        page,
        pageSize,
        filterStatus === "all" ? undefined : filterStatus
      );
      setExams(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      showToast(
        err instanceof Error ? err.message : "加载考试列表失败",
        "error"
      );
    } finally {
      setLoading(false);
    }
  }, [page, filterStatus, showToast]);

  useEffect(() => {
    loadExams();
  }, [loadExams]);

  const handlePublish = useCallback(
    async (id: number) => {
      try {
        await examApi.publish(id);
        showToast("考试已发布", "success");
        loadExams();
      } catch (err) {
        showToast(
          err instanceof Error ? err.message : "发布失败",
          "error"
        );
      }
    },
    [loadExams, showToast]
  );

  const handleClose = useCallback(
    (id: number) => {
      setConfirmDialog({
        open: true,
        title: "关闭考试",
        message: "确定要关闭此考试吗？关闭后将无法再参加考试。",
        onConfirm: async () => {
          try {
            await examApi.close(id);
            showToast("考试已关闭", "success");
            loadExams();
          } catch (err) {
            showToast(
              err instanceof Error ? err.message : "关闭失败",
              "error"
            );
          }
          setConfirmDialog(null);
        },
      });
    },
    [loadExams, showToast]
  );

  const handleDelete = useCallback(
    (id: number) => {
      setConfirmDialog({
        open: true,
        title: "删除考试",
        message: "确定要删除此考试吗？此操作不可恢复。",
        onConfirm: async () => {
          try {
            await examApi.delete(id);
            showToast("考试已删除", "success");
            loadExams();
          } catch (err) {
            showToast(
              err instanceof Error ? err.message : "删除失败",
              "error"
            );
          }
          setConfirmDialog(null);
        },
      });
    },
    [loadExams, showToast]
  );

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-6">
            <h1 className="text-lg font-semibold text-gray-900">考试列表</h1>
            <nav className="flex items-center gap-1">
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
              <button
                type="button"
                onClick={() => router.push("/reports")}
                className="rounded-lg px-3 py-1.5 text-sm text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
              >
                统计
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
            <button
              type="button"
              onClick={() => router.push("/upload")}
              className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50"
            >
              上传试卷
            </button>
            <button
              type="button"
              onClick={() => router.push("/exams/new")}
              className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-primary-700"
            >
              创建考试
            </button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-6xl px-6 py-8">
        {/* 筛选栏 */}
        <div className="mb-6 flex gap-2">
          {STATUS_FILTERS.map((filter) => (
            <button
              key={filter.value}
              type="button"
              onClick={() => {
                setFilterStatus(filter.value);
                setPage(1);
              }}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                filterStatus === filter.value
                  ? "bg-primary-100 text-primary-700"
                  : "bg-white text-gray-600 hover:bg-gray-50"
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* 加载状态 */}
        {loading && (
          <div className="flex items-center justify-center py-20 text-gray-400">
            加载中...
          </div>
        )}

        {/* 空状态 */}
        {!loading && exams.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-gray-400">
            <svg
              className="mb-4 h-16 w-16"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <p className="mb-2 text-sm">暂无考试</p>
            <button
              type="button"
              onClick={() => router.push("/exams/new")}
              className="text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              创建第一个考试
            </button>
          </div>
        )}

        {/* 考试卡片网格 */}
        {!loading && exams.length > 0 && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {exams.map((exam) => (
                <ExamCard
                  key={exam.id}
                  exam={exam}
                  onView={(id) => router.push(`/exams/${id}`)}
                  onEdit={(id) => router.push(`/exams/${id}/edit`)}
                  onPublish={handlePublish}
                  onClose={handleClose}
                  onDelete={handleDelete}
                  onStartExam={(id) => router.push(`/exams/${id}/take`)}
                />
              ))}
            </div>

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  上一页
                </button>
                <span className="px-4 py-2 text-sm text-gray-500">
                  {page} / {totalPages}
                </span>
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  下一页
                </button>
              </div>
            )}
          </>
        )}
      </main>

      {/* 确认弹窗 */}
      {confirmDialog?.open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="mx-4 w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="mb-2 text-lg font-semibold text-gray-900">
              {confirmDialog.title}
            </h3>
            <p className="mb-6 text-sm text-gray-500">
              {confirmDialog.message}
            </p>
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setConfirmDialog(null)}
                className="rounded-lg px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100"
              >
                取消
              </button>
              <button
                type="button"
                onClick={confirmDialog.onConfirm}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700"
              >
                确认
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ExamListPage() {
  return <ExamListPageContent />;
}
