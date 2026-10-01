import { http } from "./http";
import type { InspectionResult } from "../types/InspectionResult";

export function listInspectionResult(): Promise<InspectionResult[]> {
  return http.get<InspectionResult[]>("/inspection-result");
}

export function reviewInspectionResult(
  id: number,
  reviewStatus: "RECONFIRMED" | "REJECTED"
): Promise<InspectionResult> {
  return http.post<InspectionResult>(`/inspection-result/${id}/review`, {
    review_status: reviewStatus
  });
}
