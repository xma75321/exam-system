"use client";

import { useCallback, useRef, useState } from "react";
import { Upload } from "lucide-react";

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

interface FileUploaderProps {
  onFileSelected: (file: File) => void;
  uploading: boolean;
  error?: string;
}

export default function FileUploader({ onFileSelected, uploading, error }: FileUploaderProps) {
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndSelect = useCallback(
    (file: File) => {
      setValidationError(null);

      if (!file.name.endsWith(".docx")) {
        setValidationError("仅支持 .docx 格式文件");
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        setValidationError("文件大小超过 10MB 限制");
        return;
      }

      onFileSelected(file);
    },
    [onFileSelected]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragOver(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        validateAndSelect(file);
      }
    },
    [validateAndSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        validateAndSelect(file);
      }
      // Reset so the same file can be re-selected
      e.target.value = "";
    },
    [validateAndSelect]
  );

  const displayError = validationError ?? error;

  return (
    <div className="flex flex-col gap-3">
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            inputRef.current?.click();
          }
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 transition-all duration-200 ${
          dragOver
            ? "border-primary-500 bg-primary-50"
            : "border-gray-200 bg-gray-50/50 hover:border-primary-400 hover:bg-primary-50/50"
        } ${uploading ? "pointer-events-none opacity-60" : ""}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".docx"
          className="hidden"
          onChange={handleInputChange}
        />

        {uploading ? (
          <>
            <div className="mb-3 h-10 w-10 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
            <p className="text-sm font-medium text-primary-600">正在解析试卷...</p>
          </>
        ) : (
          <>
            <Upload
              className={`mb-3 h-10 w-10 transition-colors ${
                dragOver ? "text-primary-500" : "text-gray-400"
              }`}
            />
            <p className="text-sm font-medium text-gray-700">点击或拖拽上传</p>
            <p className="mt-1 text-xs text-gray-400">仅支持 .docx 格式，最大 10MB</p>
          </>
        )}
      </div>

      {displayError && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{displayError}</p>
      )}
    </div>
  );
}