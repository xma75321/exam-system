"use client";

import { useRouter } from "next/navigation";
import { FileText } from "lucide-react";
import { useToast } from "@/components/Toast";
import { useAuthStore } from "@/hooks/useAuth";
import { useUpload } from "@/hooks/useUpload";
import FileUploader from "@/components/FileUploader";
import ParsePreview from "@/components/ParsePreview";

function UploadPageContent() {
  const router = useRouter();
  const { showToast } = useToast();
  const { user, logout } = useAuthStore();
  const { uploading, parseResult, saving, error, uploadFile, confirmSave, reset } = useUpload();

  const handleConfirm = async () => {
    const success = await confirmSave();
    if (success) {
      showToast("入库成功", "success");
      router.push("/questions");
    }
  };

  const handleReset = () => {
    reset();
  };

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-6">
            <h1 className="text-lg font-semibold text-gray-900">上传试卷</h1>
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
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="flex flex-col gap-8 lg:flex-row">
          {/* Left column - Upload */}
          <div className="w-full lg:w-[480px] lg:shrink-0">
            <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-sm font-semibold text-gray-700">选择文件</h2>
              <FileUploader
                onFileSelected={uploadFile}
                uploading={uploading}
                error={error ?? undefined}
              />
            </div>
          </div>

          {/* Right column - Preview */}
          <div className="min-h-[400px] flex-1">
            <div className="h-full rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-sm font-semibold text-gray-700">解析预览</h2>
              {parseResult ? (
                <ParsePreview
                  result={parseResult}
                  saving={saving}
                  onConfirm={handleConfirm}
                  onReset={handleReset}
                />
              ) : (
                <div className="flex h-[400px] flex-col items-center justify-center text-gray-300">
                  <FileText className="mb-3 h-16 w-16" />
                  <p className="text-sm">请上传 Word 试卷文件开始</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function UploadPage() {
  return <UploadPageContent />;
}