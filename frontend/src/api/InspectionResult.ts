import { http } from "./client";
import type { InspectionResult } from "../types/InspectionResult";

export function listInspectionResult(params: { task_id?: number; device_id?: number; review_flag?: string } = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") query.set(key, String(value));
  });
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return http.get<InspectionResult[]>(`/inspection-result${suffix}`);
}

export function reviewVoidedResult(resultId: number, action: "REINSTATE" | "CONFIRM_VOID", note?: string) {
  return http.post<InspectionResult>(`/inspection-result/${resultId}/review`, { action, note });
}
