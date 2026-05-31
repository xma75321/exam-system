"use client";

import { useCallback, useState } from "react";
import { uploadApi } from "@/lib/api";
import type { ParseResult } from "@/types/question";

interface UploadState {
  file: File | null;
  uploading: boolean;
  parseResult: ParseResult | null;
  saving: boolean;
  error: string | null;
}

export function useUpload() {
  const [state, setState] = useState<UploadState>({
    file: null,
    uploading: false,
    parseResult: null,
    saving: false,
    error: null,
  });

  const uploadFile = useCallback(async (file: File) => {
    setState((prev) => ({ ...prev, file, uploading: true, error: null, parseResult: null }));

    try {
      const res = await uploadApi.uploadFile(file);
      setState((prev) => ({ ...prev, uploading: false, parseResult: res.data }));
    } catch (err) {
      const message = err instanceof Error ? err.message : "上传失败";
      setState((prev) => ({ ...prev, uploading: false, error: message }));
    }
  }, []);

  const confirmSave = useCallback(async (): Promise<boolean> => {
    if (!state.parseResult) return false;

    setState((prev) => ({ ...prev, saving: true }));

    try {
      await uploadApi.confirmSave(
        state.parseResult.filename,
        state.parseResult.questions
      );
      setState((prev) => ({ ...prev, saving: false }));
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : "入库失败";
      setState((prev) => ({ ...prev, saving: false, error: message }));
      return false;
    }
  }, [state.parseResult]);

  const reset = useCallback(() => {
    setState({
      file: null,
      uploading: false,
      parseResult: null,
      saving: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    uploadFile,
    confirmSave,
    reset,
  };
}