import type { DeviceStatus } from "../constants/DeviceStatus";

export interface FireDevice {
  id: number;
  building_id: number;
  device_code: string;
  device_type: string;
  floor: string;
  location_desc: string;
  install_date: string | null;
  status: DeviceStatus | string;
  capacity: number;
  next_maintenance_at: string | null;
}
