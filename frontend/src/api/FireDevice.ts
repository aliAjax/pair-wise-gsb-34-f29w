import { http } from "./http";
import type { FireDevice } from "../types/FireDevice";

export function listFireDevice(): Promise<FireDevice[]> {
  return http.get<FireDevice[]>("/fire-device");
}

export function createFireDevice(payload: Partial<FireDevice>): Promise<FireDevice> {
  return http.post<FireDevice>("/fire-device", payload);
}
