import { http } from "./client";
import type { DeviceOutage, OutageBatch } from "../types/DeviceOutage";

export interface OutageSubmitItem {
  device_code: string;
  start_at: string;
  end_at: string;
  reason?: string;
}

export function listOutageBatches(): Promise<OutageBatch[]> {
  return http.get<OutageBatch[]>("/device-outage/batch");
}

export function listOutages(params: { device_id?: number; status?: string } = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) query.set(key, String(value));
  });
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return http.get<DeviceOutage[]>(`/device-outage${suffix}`);
}

export function previewOccupied(deviceId: number, start_at: string, end_at: string) {
  const query = new URLSearchParams({ device_id: String(deviceId), start_at, end_at });
  return http.get<{ device_id: number; occupied_count: number; occupied_outage_ids: number[] }>(
    `/device-outage/occupied?${query.toString()}`
  );
}

export function submitOutages(payload: {
  items: OutageSubmitItem[];
  note?: string;
  fail_device_codes?: string[];
}) {
  return http.post<OutageBatch>("/device-outage", payload);
}

export function resumeOutageBatch(batchId: number) {
  return http.post<OutageBatch>(`/device-outage/batch/${batchId}/resume`);
}

export function reviewOutageDraft(outageId: number, action: "CONFIRM" | "CANCEL") {
  return http.post<DeviceOutage>(`/device-outage/${outageId}/review`, { action });
}

export function changeOutageWindow(
  outageId: number,
  payload: { start_at?: string; end_at?: string; reason?: string }
) {
  return http.patch<DeviceOutage>(`/device-outage/${outageId}/window`, payload);
}

export function cancelOutage(outageId: number) {
  return http.post<{ outage: DeviceOutage }>(`/device-outage/${outageId}/cancel`);
}
