export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ApiResponse<T> {
  code: number;
  data: T;
  message: string;
}