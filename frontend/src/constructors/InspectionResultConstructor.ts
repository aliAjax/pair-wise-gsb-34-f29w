import type { InspectionResult } from "../types/InspectionResult";

export const createDefaultInspectionResult = (
  overrides: Partial<InspectionResult> = {}
): InspectionResult => ({
  id: 1,
  task_id: 1,
  device_id: 1,
  item_code: "PRESSURE",
  result_status: "NORMAL",
  measured_value: "",
  photo_url: null,
  note: null,
  review_status: "ACTIVE",
  voided_by_window_id: null,
  reviewed_at: null,
  ...overrides
});

export const createInspectionResultForm = createDefaultInspectionResult;
export const createInspectionResultResponse = createDefaultInspectionResult;
