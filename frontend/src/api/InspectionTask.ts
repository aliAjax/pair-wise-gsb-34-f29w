import { http } from "./http";
import type { InspectionTask } from "../types/InspectionTask";
import type { TaskDeviceAssignment } from "../types/TaskDeviceAssignment";

export function listInspectionTask(): Promise<InspectionTask[]> {
  return http.get<InspectionTask[]>("/inspection-task");
}

export function listAssignments(
  taskId?: number
): Promise<TaskDeviceAssignment[]> {
  const query = taskId ? `?task_id=${taskId}` : "";
  return http.get<TaskDeviceAssignment[]>(`/inspection-task/assignments${query}`);
}

export function createInspectionTask(
  payload: Partial<InspectionTask> & { device_ids?: number[] }
): Promise<InspectionTask> {
  return http.post<InspectionTask>("/inspection-task", payload);
}
