"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import type { ExamStatus } from "@/types/exam";

const examFormSchema = z
  .object({
    title: z
      .string()
      .min(1, "请输入考试标题")
      .max(200, "标题不能超过200个字符"),
    description: z.string().optional(),
    duration_minutes: z
      .number({ required_error: "请输入考试时长" })
      .min(5, "考试时长不能少于5分钟")
      .max(300, "考试时长不能超过300分钟"),
    total_score: z
      .number({ required_error: "请输入总分" })
      .min(1, "总分不能少于1")
      .max(1000, "总分不能超过1000"),
    pass_score: z
      .number({ required_error: "请输入及格分数" })
      .min(0, "及格分数不能为负数"),
  })
  .refine((data) => data.pass_score <= data.total_score, {
    message: "及格分数不能超过总分",
    path: ["pass_score"],
  });

export type ExamFormValues = z.infer<typeof examFormSchema>;

interface ExamFormProps {
  onSubmit: (data: ExamFormValues & { status: ExamStatus }) => void;
  isSubmitting: boolean;
  selectedCount: number;
}

export default function ExamForm({
  onSubmit,
  isSubmitting,
  selectedCount,
}: ExamFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ExamFormValues>({
    resolver: zodResolver(examFormSchema),
    defaultValues: {
      title: "",
      description: "",
      duration_minutes: 60,
      total_score: 100,
      pass_score: 60,
    },
  });

  const handleFormSubmit =
    (status: ExamStatus) => (e: React.BaseSyntheticEvent) => {
      handleSubmit((data) => onSubmit({ ...data, status }))(e);
    };

  return (
    <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
      <div>
        <label
          htmlFor="exam-title"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          考试标题 <span className="text-red-500">*</span>
        </label>
        <input
          id="exam-title"
          type="text"
          {...register("title")}
          className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-sm transition-colors placeholder:text-gray-400 hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          placeholder="请输入考试标题"
        />
        {errors.title && (
          <p className="mt-1 text-xs text-red-500">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="exam-description"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          考试描述
        </label>
        <textarea
          id="exam-description"
          {...register("description")}
          rows={3}
          className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-sm transition-colors placeholder:text-gray-400 hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          placeholder="请输入考试描述（可选）"
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label
            htmlFor="exam-duration"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            考试时长（分钟） <span className="text-red-500">*</span>
          </label>
          <input
            id="exam-duration"
            type="number"
            {...register("duration_minutes", { valueAsNumber: true })}
            className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-sm transition-colors hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            min={5}
            max={300}
          />
          {errors.duration_minutes && (
            <p className="mt-1 text-xs text-red-500">
              {errors.duration_minutes.message}
            </p>
          )}
        </div>

        <div>
          <label
            htmlFor="exam-total-score"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            总分 <span className="text-red-500">*</span>
          </label>
          <input
            id="exam-total-score"
            type="number"
            {...register("total_score", { valueAsNumber: true })}
            className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-sm transition-colors hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            min={1}
            max={1000}
          />
          {errors.total_score && (
            <p className="mt-1 text-xs text-red-500">
              {errors.total_score.message}
            </p>
          )}
        </div>

        <div>
          <label
            htmlFor="exam-pass-score"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            及格分数 <span className="text-red-500">*</span>
          </label>
          <input
            id="exam-pass-score"
            type="number"
            {...register("pass_score", { valueAsNumber: true })}
            className="w-full rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-sm transition-colors hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            min={0}
          />
          {errors.pass_score && (
            <p className="mt-1 text-xs text-red-500">
              {errors.pass_score.message}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-gray-100 pt-4">
        <span className="text-sm text-gray-500">
          已选择 <span className="font-semibold text-primary-600">{selectedCount}</span> 道题目
        </span>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleFormSubmit("draft")}
            disabled={isSubmitting}
            className="rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            保存草稿
          </button>
          <button
            type="button"
            onClick={handleFormSubmit("open")}
            disabled={isSubmitting}
            className="rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            发布考试
          </button>
        </div>
      </div>
    </form>
  );
}