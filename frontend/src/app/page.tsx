import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="mb-4 text-4xl font-bold text-primary-600">
        智能考试系统
      </h1>
      <p className="mb-8 text-lg text-gray-500">
        上传 Word 试卷 → 自动解析 → 在线考试 → 即时评分
      </p>
      <Link
        href="/auth"
        className="rounded-lg bg-primary-600 px-6 py-3 text-white transition-colors hover:bg-primary-700"
      >
        开始使用
      </Link>
    </main>
  );
}
