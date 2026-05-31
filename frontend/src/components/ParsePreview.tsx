"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import type { ParseResult, QuestionType } from "@/types/question";

interface ParsePreviewProps {
  result: ParseResult | null;
  saving: boolean;
  onConfirm: () => void;
  onReset: () => void;
}

const TYPE_LABELS: Record<QuestionType, string> = {
  single: "单选题",
  multi: "多选题",
  judge: "判断题",
  fill: "填空题",
  essay: "简答题",
};

const TYPE_COLORS: Record<QuestionType, { bg: string; text: string; border: string }> = {
  single: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200" },
  multi: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200" },
  judge: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200" },
  fill: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200" },
  essay: { bg: "bg-gray-50", text: "text-gray-700", border: "border-gray-200" },
};

const TYPE_BADGE_COLORS: Record<QuestionType, string> = {
  single: "bg-blue-100 text-blue-700",
  multi: "bg-purple-100 text-purple-700",
  judge: "bg-emerald-100 text-emerald-700",
  fill: "bg-amber-100 text-amber-700",
  essay: "bg-gray-100 text-gray-700",
};

function TypeStatCard({ type, count }: { type: QuestionType; count: number }) {
  const colors = TYPE_COLORS[type];
  return (
    <div className={`flex flex-col items-center rounded-lg border ${colors.border} ${colors.bg} px-4 py-3`}>
      <span className={`text-xs font-medium ${colors.text}`}>{TYPE_LABELS[type]}</span>
      <span className={`mt-1 text-2xl font-bold ${colors.text}`}>{count}</span>
    </div>
  );
}

function QuestionItem({
  question,
  index,
}: {
  question: ParseResult["questions"][number];
  index: number;
}) {
  const [expanded, setExpanded] = useState(false);
  const badgeClass = TYPE_BADGE_COLORS[question.type];

  return (
    <div className="rounded-lg border border-gray-100 bg-white transition-shadow hover:shadow-sm">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-3 px-4 py-3 text-left"
      >
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-500">
          {index + 1}
        </span>
        <span className={`shrink-0 rounded-md px-2 py-0.5 text-xs font-medium ${badgeClass}`}>
          {TYPE_LABELS[question.type]}
        </span>
        <span className="min-w-0 flex-1 truncate text-sm text-gray-700">
          {question.content.length > 80
            ? question.content.slice(0, 80) + "..."
            : question.content}
        </span>
        <span className="shrink-0 text-xs text-gray-400">{question.score}分</span>
        {expanded ? (
          <ChevronUp className="h-4 w-4 shrink-0 text-gray-400" />
        ) : (
          <ChevronDown className="h-4 w-4 shrink-0 text-gray-400" />
        )}
      </button>

      {expanded && (
        <div className="border-t border-gray-50 px-4 pb-4 pt-3">
          <div className="space-y-2">
            <div>
              <span className="text-xs font-medium text-gray-500">题目内容</span>
              <p className="mt-0.5 text-sm text-gray-800 whitespace-pre-wrap">{question.content}</p>
            </div>

            {question.options && question.options.length > 0 && (
              <div>
                <span className="text-xs font-medium text-gray-500">选项</span>
                <div className="mt-1 space-y-1">
                  {question.options.map((opt) => (
                    <div
                      key={opt.label}
                      className={`flex items-start gap-2 rounded-md px-2 py-1 text-sm ${
                        opt.is_correct ? "bg-emerald-50 text-emerald-700" : "text-gray-600"
                      }`}
                    >
                      <span className="font-medium">{opt.label}.</span>
                      <span>{opt.content}</span>
                      {opt.is_correct && (
                        <span className="ml-auto text-xs font-medium">✓</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-6">
              <div>
                <span className="text-xs font-medium text-gray-500">答案</span>
                <p className="mt-0.5 text-sm text-gray-800">{question.answer}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-gray-500">分值</span>
                <p className="mt-0.5 text-sm text-gray-800">{question.score}分</p>
              </div>
            </div>

            {question.explanation && (
              <div>
                <span className="text-xs font-medium text-gray-500">解析</span>
                <p className="mt-0.5 text-sm text-gray-600">{question.explanation}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ParsePreview({ result, saving, onConfirm, onReset }: ParsePreviewProps) {
  if (!result) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-gray-400">
        <p className="text-sm">请上传 Word 试卷文件开始</p>
      </div>
    );
  }

  const typeEntries = (Object.entries(result.type_summary) as [QuestionType, number][]).filter(
    ([, count]) => count > 0
  );

  return (
    <div className="flex h-full flex-col gap-5">
      {/* File info */}
      <div className="rounded-lg bg-primary-50 px-4 py-3">
        <p className="text-sm font-medium text-primary-700">
          {result.filename}
        </p>
        <p className="mt-0.5 text-xs text-primary-600">
          共 {result.total_count} 道题目 · {(result.file_size / 1024).toFixed(1)} KB
        </p>
      </div>

      {/* Type statistics */}
      <div className="grid grid-cols-5 gap-2">
        {typeEntries.map(([type, count]) => (
          <TypeStatCard key={type} type={type} count={count} />
        ))}
      </div>

      {/* Question list */}
      <div className="flex-1 space-y-2 overflow-y-auto">
        {result.questions.map((q, i) => (
          <QuestionItem key={q.temp_id} question={q} index={i} />
        ))}
      </div>

      {/* Action buttons */}
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={onConfirm}
          disabled={saving}
          className="flex-1 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500/50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? "入库中..." : "确认入库"}
        </button>
        <button
          type="button"
          onClick={onReset}
          disabled={saving}
          className="rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-200 disabled:cursor-not-allowed disabled:opacity-60"
        >
          重新上传
        </button>
      </div>
    </div>
  );
}