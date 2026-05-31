export type ExamStatus = "draft" | "open" | "closed";

export interface ExamCreateRequest {
  title: string;
  description?: string;
  duration_minutes: number;
  total_score: number;
  pass_score: number;
  question_ids: number[];
}

export interface ExamResponse {
  id: number;
  title: string;
  description?: string;
  duration_minutes: number;
  total_score: number;
  pass_score: number;
  status: ExamStatus;
  question_count: number;
  created_at?: string;
}

// 考试结果相关类型
export interface QuestionResult {
  id: number;
  type: string;
  content: string;
  score: number;
  sort_order: number;
  options?: { id: number; label: string; content: string }[];
  user_answer?: string | null;
  correct_answer: string;
  earned_score?: number | null;
  is_correct?: boolean | null;
  explanation?: string | null;
}

export interface TypeStat {
  type: string;
  total: number;
  correct: number;
  pending: number;
}

export interface AttemptResult {
  id: number;
  exam_id: number;
  exam_title: string;
  status: string;
  started_at: string;
  submitted_at?: string | null;
  duration_minutes: number;
  total_score?: number | null;
  objective_score?: number | null;
  subjective_score?: number | null;
  pass_score: number;
  total_questions: number;
  correct_count: number;
  pending_count: number;
  is_passed?: boolean | null;
  questions: QuestionResult[];
  type_stats: TypeStat[];
}