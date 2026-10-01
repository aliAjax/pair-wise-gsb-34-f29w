import type { DeviceType } from "./DeviceType";

export interface FireDevice {
  id: number;
  building_id: number;
  device_code: string;
  device_type: DeviceType | string;
  floor: string;
  location_desc: string;
  install_date: string | null;
  status: "NORMAL" | "OUTAGE" | "PENDING_REUSE" | "FAULT" | string;
  next_maintenance_at: string | null;
  reuse_paperwork: string[];
}
