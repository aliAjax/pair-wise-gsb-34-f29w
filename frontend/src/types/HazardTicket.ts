import type { ReviewStatus } from "../constants/ReviewStatus";

export interface HazardTicket {
  id: number;
  result_id: number;
  severity: string;
  owner_id: number;
  deadline: string | null;
  rectify_status: string;
  rectify_note: string | null;
  closed_at: string | null;
  review_status: ReviewStatus | string;
  voided_by_window_id: number | null;
  reviewed_at: string | null;
}
