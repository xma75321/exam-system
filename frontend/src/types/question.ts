export type QuestionType = 'single' | 'multi' | 'judge' | 'fill' | 'essay';

export interface Option {
  label: string;
  content: string;
  is_correct?: boolean;
}

export interface ParsedQuestion {
  temp_id: string;
  type: QuestionType;
  content: string;
  options?: Option[];
  answer: string;
  score: number;
  explanation?: string;
}

export interface ParseResult {
  filename: string;
  file_path: string;
  file_size: number;
  total_count: number;
  questions: ParsedQuestion[];
  type_summary: Record<QuestionType, number>;
}

export interface Question {
  id: number;
  type: QuestionType;
  content: string;
  score: number;
  created_at: string;
}

export interface QuestionDetail extends Question {
  options?: Option[];
  answer: string;
  explanation?: string;
}

export interface QuestionListResponse {
  items: Question[];
  total: number;
  page: number;
  page_size: number;
}

export interface SelectedQuestion {
  id: number;
  type: QuestionType;
  content: string;
  score: number;
}