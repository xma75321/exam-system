import type { Metadata } from "next";
import "./globals.css";
import GlobalErrorBoundary from "@/components/GlobalErrorBoundary";
import { ToastProvider } from "@/components/Toast";
import AuthGuard from "@/components/AuthGuard";

export const metadata: Metadata = {
  title: "智能考试系统",
  description: "上传 Word 试卷，自动解析题目，在线考试，自动评分",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <ToastProvider>
          <AuthGuard>
            <GlobalErrorBoundary>{children}</GlobalErrorBoundary>
          </AuthGuard>
        </ToastProvider>
      </body>
    </html>
  );
}
