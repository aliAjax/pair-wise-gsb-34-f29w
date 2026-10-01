import { http } from "./client";
import type { FireDevice } from "../types/FireDevice";

export function listFireDevice(params: { building_id?: number; status?: string; device_type?: string } = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") query.set(key, String(value));
  });
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return http.get<FireDevice[]>(`/fire-device${suffix}`);
}

export function createFireDevice(payload: Partial<FireDevice> & { building_id: number; device_code: string; device_type: string; floor: string; location_desc: string }) {
  return http.post<FireDevice>("/fire-device", payload);
}

export function addReusePaperwork(deviceId: number, paperwork_items: string[]) {
  return http.post<FireDevice>(`/fire-device/${deviceId}/paperwork`, { paperwork_items });
}

export function reactivateFireDevice(deviceId: number) {
  return http.post<FireDevice>(`/fire-device/${deviceId}/reactivate`);
}
