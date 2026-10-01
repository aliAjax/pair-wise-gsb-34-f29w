import type { AssignmentStatus } from "../constants/AssignmentStatus";

export interface TaskDeviceAssignment {
  id: number;
  task_id: number;
  building_id: number;
  device_type: string;
  planned_device_id: number;
  actual_device_id: number | null;
  assignment_status: AssignmentStatus | string;
  window_id: number | null;
  origin_assignment_id: number | null;
  queue_position: number | null;
  seats: number;
}
