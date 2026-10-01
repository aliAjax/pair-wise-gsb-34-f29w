import type { FireDevice } from "../types/FireDevice";

export const createDefaultFireDevice = (overrides: Partial<FireDevice> = {}): FireDevice => ({
  id: 0,
  building_id: 1,
  device_code: "",
  device_type: "HYDRANT",
  floor: "1F",
  location_desc: "",
  install_date: null,
  status: "NORMAL",
  next_maintenance_at: null,
  reuse_paperwork: [],
  ...overrides
});

export const createFireDeviceForm = createDefaultFireDevice;
export const createFireDeviceResponse = createDefaultFireDevice;
