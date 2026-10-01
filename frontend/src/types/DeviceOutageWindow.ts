import type { OutageStatus } from "../constants/OutageStatus";
import type { WriteStage } from "../constants/ProcedureType";

export interface DeviceOutageWindow {
  id: number;
  window_group_id: number;
  version: number;
  device_id: number;
  owner_id: number;
  start_at: string;
  end_at: string;
  reason: string;
  outage_status: OutageStatus | string;
  occupied_capacity: number;
  demanded_capacity: number;
  write_stage: WriteStage | string;
  resume_key: string | null;
  last_error: string | null;
  confirmed_at: string | null;
  backup_capacity_total?: number;
  idempotent_replayed?: boolean;
}

export interface OutageWindowCreatePayload {
  device_id: number;
  owner_id: number;
  start_at: string;
  end_at: string;
  reason?: string;
}

export interface OutageChangePayload {
  start_at: string;
  end_at: string;
  reason?: string;
}

export interface CapacityHolding {
  id: number;
  window_id: number;
  backup_device_id: number;
  assignment_id: number;
  seats: number;
}

export interface OutageDraft {
  id: number;
  window_id: number;
  owner_id: number;
  payload: string;
  observed_occupied: number;
  lock_version: number;
}

export interface OutageProcedure {
  id: number;
  device_id: number;
  window_id: number;
  procedure_type: string;
  completed: boolean;
  doc_url: string | null;
}

export interface ConflictGuardResponse {
  conflict: boolean;
  window_id: number;
  occupied_capacity: number;
  backup_capacity_total: number;
  demanded_capacity: number;
  draft_saved: boolean;
  drafts: OutageDraft[];
  window?: DeviceOutageWindow;
}

export interface ChangeWindowResponse {
  superseded_window_id: number;
  new_window: DeviceOutageWindow;
  voided: {
    result_ids: number[];
    ticket_ids: number[];
    newly_voided_results: number;
  };
}
