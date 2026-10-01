export type OutageStatusValue = "DRAFT" | "CONFIRMED" | "SUPERSEDED" | "CANCELLED" | "PENDING";

export interface RerouteSummary {
  affected_slot_count: number;
  rerouted: { task_id: number; backup_device_id: number }[];
  queued: { task_id: number; device_id: number }[];
  backup_capacity: number;
}

export interface CascadeSummary {
  voided_result_ids: number[];
  voided_ticket_ids: number[];
  voided_count: number;
}

export interface DeviceOutage {
  id: number;
  batch_id: number | null;
  device_id: number;
  start_at: string;
  end_at: string;
  reason: string | null;
  status: OutageStatusValue | string;
  version: number;
  confirmed_by: number | null;
  confirmed_at: string | null;
  occupied_count: number;
  conflict_outage_ids: number[];
  occupied?: boolean;
  reroute?: RerouteSummary;
  cascade?: CascadeSummary;
}

export type OutageBatchStatusValue = "PARTIAL_FAILED" | "COMPLETED" | "RESUMED";

export interface OutageBatch {
  id: number;
  submitted_by: number;
  submitted_at: string;
  status: OutageBatchStatusValue | string;
  note: string | null;
  fail_device_codes: string[];
  items: DeviceOutage[];
}
