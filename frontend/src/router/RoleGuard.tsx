import type { Role } from "../constants/roles";
import { routes } from "./routes";
import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

// 路由守卫：按当前角色决定可访问页面
export function RoleGuard({ role, children }: { role: Role; children: ReactNode }) {
  const allowed = routes.some((route) => route.roles.includes(role));
  if (!allowed) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}
