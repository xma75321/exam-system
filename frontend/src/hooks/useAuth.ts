import { create } from "zustand";
import { authApi, setToken, removeToken } from "@/lib/api";
import type { User } from "@/types/auth";

const TOKEN_KEY = "auth_token";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;

  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: getStoredToken(),
  isLoading: false,

  login: async (username: string, password: string) => {
    set({ isLoading: true });
    try {
      console.log("useAuth.login 开始...");
      const res = await authApi.login({ username, password });
      console.log("useAuth.login API 返回:", res);
      const { access_token } = res.data;
      setToken(access_token);
      set({ token: access_token });
      console.log("Token 已保存，获取用户信息...");

      const userRes = await authApi.me();
      console.log("用户信息获取成功:", userRes.data);
      set({ user: userRes.data, isLoading: false });
    } catch (error) {
      console.error("useAuth.login 失败:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (username: string, email: string, password: string) => {
    set({ isLoading: true });
    try {
      console.log("useAuth.register 开始...");
      const res = await authApi.register({ username, email, password });
      console.log("useAuth.register 成功:", res);
      set({ isLoading: false });
    } catch (error) {
      console.error("useAuth.register 失败:", error);
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    removeToken();
    set({ user: null, token: null });
  },

  checkAuth: async () => {
    const storedToken = getStoredToken();
    if (!storedToken) {
      set({ user: null, token: null });
      return;
    }
    set({ token: storedToken, isLoading: true });
    try {
      const res = await authApi.me();
      set({ user: res.data, isLoading: false });
    } catch {
      removeToken();
      set({ user: null, token: null, isLoading: false });
    }
  },
}));