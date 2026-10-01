import type { HazardSeverity } from "./HazardSeverity";

export type RectifyStatus =
  | "OPEN"
  | "ASSIGNED"
  | "RECTIFIED"
  | "VERIFIED"
  | "VOID_PENDING_REVIEW"
  | "VOID_CONFIRMED";

export interface HazardTicket {
  id: number;
  result_id: number;
  device_id: number;
  severity: HazardSeverity | string;
  owner_id: number | null;
  deadline: string | null;
  rectify_status: RectifyStatus | string;
  rectify_note: string | null;
  closed_at: string | null;
  voided_at: string | null;
  voided_by_outage_id: number | null;
}
