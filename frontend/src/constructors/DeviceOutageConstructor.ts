import type { DeviceOutage, OutageBatch } from "../types/DeviceOutage";

export const createDefaultDeviceOutage = (overrides: Partial<DeviceOutage> = {}): DeviceOutage => ({
  id: 0,
  batch_id: null,
  device_id: 0,
  start_at: "",
  end_at: "",
  reason: null,
  status: "DRAFT",
  version: 1,
  confirmed_by: null,
  confirmed_at: null,
  occupied_count: 0,
  conflict_outage_ids: [],
  ...overrides
});

export const createDefaultOutageBatch = (overrides: Partial<OutageBatch> = {}): OutageBatch => ({
  id: 0,
  submitted_by: 0,
  submitted_at: "",
  status: "PARTIAL_FAILED",
  note: null,
  fail_device_codes: [],
  items: [],
  ...overrides
});

// 停用表单默认行
export const createOutageSubmitItem = () => ({
  device_code: "",
  start_at: "",
  end_at: "",
  reason: ""
});

export const createDeviceOutageForm = createDefaultDeviceOutage;
export const createDeviceOutageResponse = createDefaultDeviceOutage;
