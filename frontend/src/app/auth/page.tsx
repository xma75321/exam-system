"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuthStore } from "@/hooks/useAuth";
import { useToast } from "@/components/Toast";

const loginSchema = z.object({
  username: z.string().min(1, "请输入用户名"),
  password: z.string().min(1, "请输入密码"),
});

type LoginForm = z.infer<typeof loginSchema>;

const registerSchema = z
  .object({
    username: z
      .string()
      .min(3, "用户名至少3个字符")
      .max(50, "用户名最多50个字符"),
    email: z.string().email("请输入有效的邮箱地址"),
    password: z
      .string()
      .min(6, "密码至少6个字符")
      .max(20, "密码最多20个字符"),
    confirmPassword: z.string().min(1, "请确认密码"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "两次输入的密码不一致",
    path: ["confirmPassword"],
  });

type RegisterForm = z.infer<typeof registerSchema>;

type Tab = "login" | "register";

export default function AuthPage() {
  const [activeTab, setActiveTab] = useState<Tab>("login");
  const { login, register, isLoading } = useAuthStore();
  const { showToast } = useToast();
  const router = useRouter();

  const loginForm = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: "", password: "" },
  });

  const registerForm = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onLogin = async (data: LoginForm) => {
    try {
      console.log("开始登录...", data.username);
      await login(data.username, data.password);
      console.log("登录成功，准备跳转...");
      showToast("登录成功", "success");
      router.push("/exams");
    } catch (err) {
      console.error("登录失败:", err);
      const message = err instanceof Error ? err.message : "登录失败";
      showToast(message, "error");
    }
  };

  const onRegister = async (data: RegisterForm) => {
    try {
      console.log("开始注册...", data.username, data.email);
      const res = await register(data.username, data.email, data.password);
      console.log("注册成功!", res);
      showToast("注册成功，请登录", "success");
      setActiveTab("login");
      loginForm.setValue("username", data.username);
      registerForm.reset();
    } catch (err) {
      console.error("注册失败:", err);
      const message = err instanceof Error ? err.message : "注册失败";
      showToast(message, "error");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-100 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-primary-700">智能考试系统</h1>
          <p className="mt-2 text-sm text-gray-500">上传试卷，在线考试，自动评分</p>
        </div>

        {/* Card */}
        <div className="rounded-xl bg-white shadow-xl shadow-primary-100/50">
          {/* Tabs */}
          <div className="flex border-b border-gray-100">
            <button
              type="button"
              onClick={() => setActiveTab("login")}
              className={`flex-1 py-3.5 text-sm font-semibold transition-colors ${
                activeTab === "login"
                  ? "border-b-2 border-primary-600 text-primary-600"
                  : "text-gray-400 hover:text-gray-600"
              }`}
            >
              登录
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("register")}
              className={`flex-1 py-3.5 text-sm font-semibold transition-colors ${
                activeTab === "register"
                  ? "border-b-2 border-primary-600 text-primary-600"
                  : "text-gray-400 hover:text-gray-600"
              }`}
            >
              注册
            </button>
          </div>

          {/* Login Form */}
          {activeTab === "login" && (
            <form onSubmit={loginForm.handleSubmit(onLogin)} className="p-6 space-y-4">
              <div>
                <label htmlFor="login-username" className="mb-1.5 block text-sm font-medium text-gray-700">
                  用户名
                </label>
                <input
                  id="login-username"
                  type="text"
                  placeholder="请输入用户名"
                  autoComplete="username"
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 ${
                    loginForm.formState.errors.username
                      ? "border-red-300 focus:border-red-500 focus:ring-red-500/20"
                      : "border-gray-200"
                  }`}
                  {...loginForm.register("username")}
                />
                {loginForm.formState.errors.username && (
                  <p className="mt-1 text-xs text-red-500">
                    {loginForm.formState.errors.username.message}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="login-password" className="mb-1.5 block text-sm font-medium text-gray-700">
                  密码
                </label>
                <input
                  id="login-password"
                  type="password"
                  placeholder="请输入密码"
                  autoComplete="current-password"
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 ${
                    loginForm.formState.errors.password
                      ? "border-red-300 focus:border-red-500 focus:ring-red-500/20"
                      : "border-gray-200"
                  }`}
                  {...loginForm.register("password")}
                />
                {loginForm.formState.errors.password && (
                  <p className="mt-1 text-xs text-red-500">
                    {loginForm.formState.errors.password.message}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-primary-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500/50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? "登录中..." : "登录"}
              </button>
            </form>
          )}

          {/* Register Form */}
          {activeTab === "register" && (
            <form onSubmit={registerForm.handleSubmit(onRegister)} className="p-6 space-y-4">
              <div>
                <label htmlFor="reg-username" className="mb-1.5 block text-sm font-medium text-gray-700">
                  用户名
                </label>
                <input
                  id="reg-username"
                  type="text"
                  placeholder="3-50个字符"
                  autoComplete="username"
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 ${
                    registerForm.formState.errors.username
                      ? "border-red-300 focus:border-red-500 focus:ring-red-500/20"
                      : "border-gray-200"
                  }`}
                  {...registerForm.register("username")}
                />
                {registerForm.formState.errors.username && (
                  <p className="mt-1 text-xs text-red-500">
                    {registerForm.formState.errors.username.message}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="reg-email" className="mb-1.5 block text-sm font-medium text-gray-700">
                  邮箱
                </label>
                <input
                  id="reg-email"
                  type="email"
                  placeholder="example@mail.com"
                  autoComplete="email"
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 ${
                    registerForm.formState.errors.email
                      ? "border-red-300 focus:border-red-500 focus:ring-red-500/20"
                      : "border-gray-200"
                  }`}
                  {...registerForm.register("email")}
                />
                {registerForm.formState.errors.email && (
                  <p className="mt-1 text-xs text-red-500">
                    {registerForm.formState.errors.email.message}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="reg-password" className="mb-1.5 block text-sm font-medium text-gray-700">
                  密码
                </label>
                <input
                  id="reg-password"
                  type="password"
                  placeholder="6-20个字符"
                  autoComplete="new-password"
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 ${
                    registerForm.formState.errors.password
                      ? "border-red-300 focus:border-red-500 focus:ring-red-500/20"
                      : "border-gray-200"
                  }`}
                  {...registerForm.register("password")}
                />
                {registerForm.formState.errors.password && (
                  <p className="mt-1 text-xs text-red-500">
                    {registerForm.formState.errors.password.message}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="reg-confirm" className="mb-1.5 block text-sm font-medium text-gray-700">
                  确认密码
                </label>
                <input
                  id="reg-confirm"
                  type="password"
                  placeholder="再次输入密码"
                  autoComplete="new-password"
                  className={`w-full rounded-lg border px-3.5 py-2.5 text-sm transition-colors focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 ${
                    registerForm.formState.errors.confirmPassword
                      ? "border-red-300 focus:border-red-500 focus:ring-red-500/20"
                      : "border-gray-200"
                  }`}
                  {...registerForm.register("confirmPassword")}
                />
                {registerForm.formState.errors.confirmPassword && (
                  <p className="mt-1 text-xs text-red-500">
                    {registerForm.formState.errors.confirmPassword.message}
                  </p>
                )}
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-primary-600 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500/50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoading ? "注册中..." : "注册"}
              </button>
            </form>
          )}
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-gray-400">
          智能考试系统 MVP
        </p>
      </div>
    </div>
  );
}