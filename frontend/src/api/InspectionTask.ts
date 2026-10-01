import { http } from "./client";
import type { InspectionTask } from "../types/InspectionTask";

export function listInspectionTask(params: { status?: string; building_id?: number } = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) query.set(key, String(value));
  });
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return http.get<InspectionTask[]>(`/inspection-task${suffix}`);
}

export function createInspectionTask(
  payload: { building_id: number; plan_date: string; task_type: string; inspector_id?: number }
) {
  return http.post<InspectionTask>("/inspection-task", payload);
}

export function changeInspectionTaskStatus(taskId: number, status: string) {
  return http.patch<InspectionTask>(`/inspection-task/${taskId}/status`, { status });
}
