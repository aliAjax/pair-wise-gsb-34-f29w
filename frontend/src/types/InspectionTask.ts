import type { InspectionStatus } from "./InspectionStatus";

export interface InspectionTask {
  id: number;
  building_id: number;
  inspector_id: number | null;
  plan_date: string;
  task_type: string;
  status: InspectionStatus | string;
  checklist_version: string;
  finished_at: string | null;
  result_count?: number;
  voided_count?: number;
}
