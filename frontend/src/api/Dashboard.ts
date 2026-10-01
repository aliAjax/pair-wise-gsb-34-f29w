import { http } from "./client";
import type { AuditLog, DashboardSummary } from "../types/Dashboard";

export function getDashboardSummary(): Promise<DashboardSummary> {
  return http.get<DashboardSummary>("/dashboard/summary");
}

export function listAuditLogs(limit = 80): Promise<AuditLog[]> {
  return http.get<AuditLog[]>(`/dashboard/audit-logs?limit=${limit}`);
}
