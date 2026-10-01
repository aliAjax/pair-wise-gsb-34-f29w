import { http } from "./http";
import type { HazardTicket } from "../types/HazardTicket";

export function listHazardTicket(): Promise<HazardTicket[]> {
  return http.get<HazardTicket[]>("/hazard-ticket");
}

export function reviewHazardTicket(
  id: number,
  reviewStatus: "RECONFIRMED" | "REJECTED"
): Promise<HazardTicket> {
  return http.post<HazardTicket>(`/hazard-ticket/${id}/review`, {
    review_status: reviewStatus
  });
}
