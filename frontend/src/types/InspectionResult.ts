import type { ReviewStatus } from "../constants/ReviewStatus";

export interface InspectionResult {
  id: number;
  task_id: number;
  device_id: number;
  item_code: string;
  result_status: string;
  measured_value: string;
  photo_url: string | null;
  note: string | null;
  review_status: ReviewStatus | string;
  voided_by_window_id: number | null;
  reviewed_at: string | null;
}
