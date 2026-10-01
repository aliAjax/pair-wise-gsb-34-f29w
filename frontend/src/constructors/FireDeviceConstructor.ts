import type { FireDevice } from "../types/FireDevice";

export const createDefaultFireDevice = (
  overrides: Partial<FireDevice> = {}
): FireDevice => ({
  id: 1,
  building_id: 1,
  device_code: "FE-001",
  device_type: "EXTINGUISHER",
  floor: "1",
  location_desc: "1F 大厅",
  install_date: null,
  status: "NORMAL",
  capacity: 3,
  next_maintenance_at: null,
  ...overrides
});

export const createFireDeviceForm = createDefaultFireDevice;
export const createFireDeviceResponse = createDefaultFireDevice;
