"use client";

import type { QuestionType, Option } from "@/types/question";

interface AnswerInputProps {
  type: QuestionType;
  options?: Option[];
  value: string;
  onChange: (value: string) => void;
}

export default function AnswerInput({
  type,
  options,
  value,
  onChange,
}: AnswerInputProps) {
  switch (type) {
    case "single":
      return <SingleChoiceInput options={options ?? []} value={value} onChange={onChange} />;
    case "multi":
      return <MultiChoiceInput options={options ?? []} value={value} onChange={onChange} />;
    case "judge":
      return <JudgeInput value={value} onChange={onChange} />;
    case "fill":
      return <FillInput value={value} onChange={onChange} />;
    case "essay":
      return <EssayInput value={value} onChange={onChange} />;
    default:
      return null;
  }
}

function SingleChoiceInput({
  options,
  value,
  onChange,
}: {
  options: Option[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="space-y-2">
      {options.map((opt) => (
        <label
          key={opt.label}
          className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors ${
            value === opt.label
              ? "border-primary-500 bg-primary-50"
              : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
          }`}
        >
          <input
            type="radio"
            name="single-choice"
            value={opt.label}
            checked={value === opt.label}
            onChange={() => onChange(opt.label)}
            className="h-4 w-4 border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="font-medium text-gray-700">{opt.label}.</span>
          <span className="text-gray-600">{opt.content}</span>
        </label>
      ))}
    </div>
  );
}

function MultiChoiceInput({
  options,
  value,
  onChange,
}: {
  options: Option[];
  value: string;
  onChange: (v: string) => void;
}) {
  const selected = value ? value.split(",").filter(Boolean) : [];

  const handleToggle = (label: string) => {
    const newSelected = selected.includes(label)
      ? selected.filter((s) => s !== label)
      : [...selected, label].sort();
    onChange(newSelected.join(","));
  };

  return (
    <div className="space-y-2">
      {options.map((opt) => (
        <label
          key={opt.label}
          className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors ${
            selected.includes(opt.label)
              ? "border-primary-500 bg-primary-50"
              : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
          }`}
        >
          <input
            type="checkbox"
            value={opt.label}
            checked={selected.includes(opt.label)}
            onChange={() => handleToggle(opt.label)}
            className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="font-medium text-gray-700">{opt.label}.</span>
          <span className="text-gray-600">{opt.content}</span>
        </label>
      ))}
    </div>
  );
}

function JudgeInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex gap-4">
      {[
        { label: "正确", value: "正确" },
        { label: "错误", value: "错误" },
      ].map((opt) => (
        <label
          key={opt.value}
          className={`flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-lg border p-4 transition-colors ${
            value === opt.value
              ? "border-primary-500 bg-primary-50"
              : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
          }`}
        >
          <input
            type="radio"
            name="judge"
            value={opt.value}
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
            className="h-4 w-4 border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="font-medium text-gray-700">{opt.label}</span>
        </label>
      ))}
    </div>
  );
}

function FillInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="请输入答案"
      className="w-full rounded-lg border border-gray-200 px-4 py-3 text-gray-700 shadow-sm transition-colors placeholder:text-gray-400 hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
    />
  );
}

function EssayInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="请输入答案"
      rows={6}
      className="w-full rounded-lg border border-gray-200 px-4 py-3 text-gray-700 shadow-sm transition-colors placeholder:text-gray-400 hover:border-primary-400 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
    />
  );
}
