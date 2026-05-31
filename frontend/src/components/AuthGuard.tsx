"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/hooks/useAuth";

// 不需要登录的页面
const PUBLIC_PATHS = ["/auth", "/"];

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { token, checkAuth } = useAuthStore();

  useEffect(() => {
    // 公开页面不需要检查
    if (PUBLIC_PATHS.includes(pathname)) {
      return;
    }

    // 检查是否有 token
    if (!token) {
      router.push("/auth");
      return;
    }

    // 验证 token 是否有效
    checkAuth().catch(() => {
      router.push("/auth");
    });
  }, [pathname, token, router, checkAuth]);

  // 公开页面直接显示
  if (PUBLIC_PATHS.includes(pathname)) {
    return <>{children}</>;
  }

  // 没有 token 不显示内容
  if (!token) {
    return null;
  }

  return <>{children}</>;
}
