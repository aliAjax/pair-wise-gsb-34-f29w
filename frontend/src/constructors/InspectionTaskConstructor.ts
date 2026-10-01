import type { InspectionTask } from "../types/InspectionTask";

export const createDefaultInspectionTask = (
  overrides: Partial<InspectionTask> = {}
): InspectionTask => ({
  id: 0,
  building_id: 1,
  inspector_id: null,
  plan_date: "2026-10-10T09:00:00",
  task_type: "EXTINGUISHER",
  status: "PLANNED",
  checklist_version: "v2026.1",
  finished_at: null,
  ...overrides
});

export const createInspectionTaskForm = createDefaultInspectionTask;
export const createInspectionTaskResponse = createDefaultInspectionTask;
