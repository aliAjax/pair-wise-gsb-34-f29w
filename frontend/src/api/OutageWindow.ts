import { http } from "./http";
import type {
  CapacityHolding,
  ChangeWindowResponse,
  ConflictGuardResponse,
  DeviceOutageWindow,
  OutageChangePayload,
  OutageDraft,
  OutageProcedure,
  OutageWindowCreatePayload,
} from "../types/DeviceOutageWindow";
import type { TaskDeviceAssignment } from "../types/TaskDeviceAssignment";

const BASE = "/outage-window";

export function listOutageWindows(): Promise<DeviceOutageWindow[]> {
  return http.get<DeviceOutageWindow[]>(BASE);
}

export function getOutageWindow(id: number): Promise<DeviceOutageWindow> {
  return http.get<DeviceOutageWindow>(`${BASE}/${id}`);
}

export function submitOutageWindow(
  payload: OutageWindowCreatePayload
): Promise<DeviceOutageWindow> {
  return http.post<DeviceOutageWindow>(BASE, payload);
}

export function confirmOutageWindow(id: number): Promise<DeviceOutageWindow> {
  return http.post<DeviceOutageWindow>(`${BASE}/${id}/confirm`);
}

// 两个负责人同时确认重叠时段：容量不足时后到者看到占用数量并保留草稿
export function confirmWithConflictGuard(
  id: number,
  ownerId: number
): Promise<ConflictGuardResponse> {
  return http.post<ConflictGuardResponse>(
    `${BASE}/${id}/confirm-guard?owner_id=${ownerId}`
  );
}

// 写入失败后恢复：凭 resume_key 从断点阶段续跑
export function resumeOutageWindow(
  id: number,
  resumeKey: string
): Promise<DeviceOutageWindow> {
  return http.post<DeviceOutageWindow>(
    `${BASE}/${id}/resume?resume_key=${encodeURIComponent(resumeKey)}`
  );
}

export function changeOutageWindow(
  id: number,
  payload: OutageChangePayload
): Promise<ChangeWindowResponse> {
  return http.post<ChangeWindowResponse>(`${BASE}/${id}/change`, payload);
}

export function listWindowHoldings(id: number): Promise<CapacityHolding[]> {
  return http.get<CapacityHolding[]>(`${BASE}/${id}/holdings`);
}

export function listWindowAssignments(
  id: number
): Promise<TaskDeviceAssignment[]> {
  return http.get<TaskDeviceAssignment[]>(`${BASE}/${id}/assignments`);
}

export function listOutageDrafts(id: number): Promise<OutageDraft[]> {
  return http.get<OutageDraft[]>(`${BASE}/${id}/drafts`);
}

export function registerProcedure(
  windowId: number,
  procedureType: string,
  docUrl?: string
): Promise<OutageProcedure> {
  return http.post<OutageProcedure>(`${BASE}/${windowId}/procedure`, {
    procedure_type: procedureType,
    doc_url: docUrl ?? null
  });
}

export function listProcedures(windowId: number): Promise<OutageProcedure[]> {
  return http.get<OutageProcedure[]>(`${BASE}/${windowId}/procedures`);
}

export function restoreDevice(deviceId: number): Promise<{
  device_id: number;
  device_code: string;
  status: string;
  rescheduled: number;
}> {
  return http.post(`/outage-window/device/${deviceId}/restore`);
}
