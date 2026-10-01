export interface DashboardSummary {
  device_total: number;
  device_status_distribution: Record<string, number>;
  task_total: number;
  task_status_distribution: Record<string, number>;
  inspection_completion_rate: number;
  open_ticket_count: number;
  critical_ticket_count: number;
  void_pending_ticket_count: number;
  pending_makeup_task_ids: number[];
  outage_confirmed_count: number;
  outage_draft_count: number;
  outage_pending_count: number;
  backup_slot_capacity: number;
}

export interface AuditLog {
  id: number;
  actor: string;
  action: string;
  target_type: string;
  target_id: string | null;
  detail: string | null;
  created_at: string | null;
}
