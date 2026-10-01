import { http } from "./client";
import type { HazardTicket } from "../types/HazardTicket";

export function listHazardTicket(params: { rectify_status?: string; device_id?: number } = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) query.set(key, String(value));
  });
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return http.get<HazardTicket[]>(`/hazard-ticket${suffix}`);
}

export function createHazardTicket(payload: { result_id: number; severity: string; owner_id?: number; deadline?: string }) {
  return http.post<HazardTicket>("/hazard-ticket", payload);
}

export function dispatchHazardTicket(ticketId: number, ownerId: number) {
  return http.post<HazardTicket>(`/hazard-ticket/${ticketId}/dispatch?owner_id=${ownerId}`);
}

export function rectifyHazardTicket(ticketId: number, rectify_note: string) {
  return http.post<HazardTicket>(`/hazard-ticket/${ticketId}/rectify`, { rectify_note });
}

export function reviewOrCloseHazardTicket(
  ticketId: number,
  action: "REINSTATE" | "CONFIRM_VOID" | "CLOSE",
  rectify_note?: string
) {
  return http.post<HazardTicket>(`/hazard-ticket/${ticketId}/review`, { action, rectify_note });
}
