export type ResultReviewFlag = "ACTIVE" | "VOID_PENDING_REVIEW" | "VOID_CONFIRMED";

export interface InspectionResult {
  id: number;
  task_id: number;
  device_id: number;
  item_code: string;
  result_status: "NORMAL" | "ABNORMAL" | string;
  measured_value: string | null;
  photo_url: string | null;
  note: string | null;
  review_flag: ResultReviewFlag | string;
  voided_at: string | null;
  voided_by_outage_id: number | null;
}
