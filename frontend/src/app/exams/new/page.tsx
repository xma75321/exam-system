"use client";

import { useCallback, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/Toast";
import ExamForm, { type ExamFormValues } from "@/components/ExamForm";
import QuestionSelector from "@/components/QuestionSelector";
import SelectedQuestions from "@/components/SelectedQuestions";
import { examApi, questionApi } from "@/lib/api";
import type { ExamStatus } from "@/types/exam";
import type { Question, SelectedQuestion } from "@/types/question";

function NewExamPageContent() {
  const router = useRouter();
  const { showToast } = useToast();

  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [selectedQuestions, setSelectedQuestions] = useState<SelectedQuestion[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 同步选中的题目详情
  const syncQuestions = useCallback(
    async (ids: number[]) => {
      const existingMap = new Map(selectedQuestions.map((q) => [q.id, q]));

      const newQuestions: SelectedQuestion[] = [];
      for (const id of ids) {
        if (existingMap.has(id)) {
          newQuestions.push(existingMap.get(id)!);
        } else {
          try {
            const res = await questionApi.getDetail(id);
            const q = res.data;
            newQuestions.push({
              id: q.id,
              type: q.type,
              content: q.content,
              score: q.score,
            });
          } catch {
            // 忽略加载失败的题目
          }
        }
      }
      setSelectedQuestions(newQuestions);
    },
    [selectedQuestions]
  );

  const handleSelectionChange = useCallback(
    (ids: number[]) => {
      setSelectedIds(ids);
      syncQuestions(ids);
    },
    [syncQuestions]
  );

  const handleReorder = useCallback((fromIndex: number, toIndex: number) => {
    setSelectedQuestions((prev) => {
      const newQuestions = [...prev];
      const [moved] = newQuestions.splice(fromIndex, 1);
      newQuestions.splice(toIndex, 0, moved);
      return newQuestions;
    });
  }, []);

  const handleScoreChange = useCallback((id: number, score: number) => {
    setSelectedQuestions((prev) =>
      prev.map((q) => (q.id === id ? { ...q, score } : q))
    );
  }, []);

  const handleRemove = useCallback((id: number) => {
    setSelectedIds((prev) => prev.filter((sid) => sid !== id));
    setSelectedQuestions((prev) => prev.filter((q) => q.id !== id));
  }, []);

  const handleSubmit = useCallback(
    async (data: ExamFormValues & { status: ExamStatus }) => {
      if (selectedQuestions.length === 0) {
        showToast("请至少选择一道题目", "error");
        return;
      }

      setIsSubmitting(true);
      try {
        // 后端 ExamCreate 不接受 status 字段，总是创建 draft
        const createData = {
          title: data.title,
          description: data.description,
          duration_minutes: data.duration_minutes,
          total_score: data.total_score,
          pass_score: data.pass_score,
          question_ids: selectedQuestions.map((q) => q.id),
        };
        const res = await examApi.create(createData);

        // 如果用户选择"发布考试"，则调用 publish API
        if (data.status === "open") {
          await examApi.publish(res.data.id);
          showToast("考试已发布", "success");
        } else {
          showToast("草稿已保存", "success");
        }

        router.push("/exams");
      } catch (err) {
        showToast(
          err instanceof Error ? err.message : "创建失败，请重试",
          "error"
        );
      } finally {
        setIsSubmitting(false);
      }
    },
    [selectedQuestions, router, showToast]
  );

  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white">
        <div className="mx-auto flex h-16 max-w-6xl items-center px-6">
          <h1 className="text-lg font-semibold text-gray-900">创建考试</h1>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="flex flex-col gap-8">
          {/* 上方：考试表单 */}
          <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-sm font-semibold text-gray-700">
              考试信息
            </h2>
            <ExamForm
              onSubmit={handleSubmit}
              isSubmitting={isSubmitting}
              selectedCount={selectedQuestions.length}
            />
          </div>

          {/* 下方：选题区 */}
          <div className="flex flex-col gap-6 lg:flex-row">
            {/* 左侧：题目选择器 */}
            <div className="min-h-[500px] flex-1">
              <QuestionSelector
                selectedIds={selectedIds}
                onSelectionChange={handleSelectionChange}
              />
            </div>

            {/* 右侧：已选题目 */}
            <div className="min-h-[500px] flex-1">
              <SelectedQuestions
                questions={selectedQuestions}
                onReorder={handleReorder}
                onScoreChange={handleScoreChange}
                onRemove={handleRemove}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function NewExamPage() {
  return <NewExamPageContent />;
}
