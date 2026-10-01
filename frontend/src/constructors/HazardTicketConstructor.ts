import type { HazardTicket } from "../types/HazardTicket";

export const createDefaultHazardTicket = (
  overrides: Partial<HazardTicket> = {}
): HazardTicket => ({
  id: 1,
  result_id: 1,
  severity: "MEDIUM",
  owner_id: 1,
  deadline: null,
  rectify_status: "OPEN",
  rectify_note: null,
  closed_at: null,
  review_status: "ACTIVE",
  voided_by_window_id: null,
  reviewed_at: null,
  ...overrides
});

export const createHazardTicketForm = createDefaultHazardTicket;
export const createHazardTicketResponse = createDefaultHazardTicket;
