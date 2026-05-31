import type { ApiResponse, LoginRequest, RegisterRequest, TokenResponse, User } from "@/types/auth";
import type { ParseResult, ParsedQuestion, QuestionDetail, QuestionListResponse, QuestionType } from "@/types/question";
import type { ExamCreateRequest, ExamResponse, AttemptResult } from "@/types/exam";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

const TOKEN_KEY = "auth_token";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<ApiResponse<T>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401) {
    removeToken();
    const errorData = await response.json().catch(() => null);
    // 后端返回 {"detail": {"code": 1003, "message": "用户名或密码错误"}}
    const message = errorData?.detail?.message ?? errorData?.message ?? "未授权，请重新登录";
    if (typeof window !== "undefined" && message.includes("未授权")) {
      window.location.href = "/auth";
    }
    throw new Error(message);
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const message =
      errorData?.detail?.message ?? errorData?.message ?? `请求失败 (${response.status})`;
    throw new Error(message);
  }

  return response.json();
}

export const authApi = {
  register(data: RegisterRequest): Promise<ApiResponse<User>> {
    return request("POST", "/auth/register", data);
  },

  login(data: LoginRequest): Promise<ApiResponse<TokenResponse>> {
    return request("POST", "/auth/login", data);
  },

  me(): Promise<ApiResponse<User>> {
    return request("GET", "/auth/me");
  },
};

interface ConfirmSaveResult {
  exam_id: number;
  questions: { id: number }[];
}

export const uploadApi = {
  async uploadFile(file: File): Promise<ApiResponse<ParseResult>> {
    const formData = new FormData();
    formData.append("file", file);

    const token = getToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${BASE_URL}/upload`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (response.status === 401) {
      removeToken();
      if (typeof window !== "undefined") {
        window.location.href = "/auth";
      }
      throw new Error("未授权，请重新登录");
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const message =
        errorData?.message ?? `请求失败 (${response.status})`;
      throw new Error(message);
    }

    return response.json();
  },

  confirmSave(
    filename: string,
    questions: ParsedQuestion[]
  ): Promise<ApiResponse<ConfirmSaveResult>> {
    return request("POST", "/upload/confirm", { filename, questions });
  },
};

export const questionApi = {
  list(
    page: number,
    pageSize: number,
    type?: QuestionType
  ): Promise<ApiResponse<QuestionListResponse>> {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    });
    if (type) {
      params.set("type", type);
    }
    return request("GET", `/questions?${params.toString()}`);
  },

  getDetail(id: number): Promise<ApiResponse<QuestionDetail>> {
    return request("GET", `/questions/${id}`);
  },
};

export interface AttemptStartResponse {
  id: number;
  exam_id: number;
  exam_title: string;
  status: string;
  started_at: string;
  duration_minutes: number;
  questions: AttemptQuestion[];
}

export interface AttemptQuestion {
  id: number;
  type: string;
  content: string;
  score: number;
  sort_order: number;
  options?: { id: number; label: string; content: string }[];
}

export interface AttemptProgressResponse {
  id: number;
  exam_id: number;
  exam_title: string;
  status: string;
  started_at: string;
  duration_minutes: number;
  questions: AttemptQuestion[];
  answered: { question_id: number; user_answer: string }[];
}

export const attemptApi = {
  start(examId: number): Promise<ApiResponse<AttemptStartResponse>> {
    return request("POST", "/attempts", { exam_id: examId });
  },

  getProgress(attemptId: number): Promise<ApiResponse<AttemptProgressResponse>> {
    return request("GET", `/attempts/${attemptId}`);
  },

  saveAnswers(
    attemptId: number,
    answers: { question_id: number; user_answer: string }[]
  ): Promise<ApiResponse<null>> {
    return request("PUT", `/attempts/${attemptId}/answers`, { answers });
  },

  submit(attemptId: number): Promise<ApiResponse<{ id: number; status: string; submitted_at: string }>> {
    return request("POST", `/attempts/${attemptId}/submit`);
  },

  getResult(attemptId: number): Promise<ApiResponse<AttemptResult>> {
    return request("GET", `/attempts/${attemptId}/result`);
  },
};

export const examApi = {
  create(data: ExamCreateRequest): Promise<ApiResponse<ExamResponse>> {
    return request("POST", "/exams", data);
  },

  publish(id: number): Promise<ApiResponse<{ id: number; status: string }>> {
    return request("POST", `/exams/${id}/publish`);
  },

  close(id: number): Promise<ApiResponse<{ id: number; status: string }>> {
    return request("POST", `/exams/${id}/close`);
  },

  delete(id: number): Promise<ApiResponse<null>> {
    return request("DELETE", `/exams/${id}`);
  },

  list(
    page: number,
    pageSize: number,
    status?: string
  ): Promise<ApiResponse<{ items: ExamResponse[]; total: number; page: number; page_size: number }>> {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    });
    if (status) {
      params.set("status", status);
    }
    return request("GET", `/exams?${params.toString()}`);
  },
};

export interface ReportOverview {
  total_attempts: number;
  average_score: number;
  max_score: number;
  pass_rate: number;
}

export interface TrendData {
  date: string;
  score: number;
  exam_title: string;
  pass_score: number;
}

export const reportApi = {
  getOverview(): Promise<ApiResponse<ReportOverview>> {
    return request("GET", "/reports/overview");
  },

  getTrend(days: number = 30): Promise<ApiResponse<TrendData[]>> {
    return request("GET", `/reports/trend?days=${days}`);
  },
};