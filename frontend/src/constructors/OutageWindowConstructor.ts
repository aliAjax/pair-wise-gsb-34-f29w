import type {
  DeviceOutageWindow,
  OutageWindowCreatePayload,
} from "../types/DeviceOutageWindow";

// 默认停用时段草稿：页面与 store 不得散写默认结构
export const createDefaultOutageWindow = (
  overrides: Partial<DeviceOutageWindow> = {}
): DeviceOutageWindow => ({
  id: 0,
  window_group_id: 0,
  version: 1,
  device_id: 1,
  owner_id: 100,
  start_at: "2026-10-10T08:00:00",
  end_at: "2026-10-10T18:00:00",
  reason: "",
  outage_status: "DRAFT",
  occupied_capacity: 0,
  demanded_capacity: 0,
  write_stage: "PERSIST_WINDOW",
  resume_key: null,
  last_error: null,
  confirmed_at: null,
  ...overrides
});

// 表单对象（提交停用时段）
export const createOutageWindowForm = (
  overrides: Partial<OutageWindowCreatePayload> = {}
): OutageWindowCreatePayload => ({
  device_id: 1,
  owner_id: 100,
  start_at: "2026-10-10T08:00:00",
  end_at: "2026-10-10T18:00:00",
  reason: "",
  ...overrides
});

// 后端响应 -> 页面模型
export const createOutageWindowResponse = (
  raw: Partial<DeviceOutageWindow>
): DeviceOutageWindow => ({
  ...createDefaultOutageWindow(),
  ...raw
});
