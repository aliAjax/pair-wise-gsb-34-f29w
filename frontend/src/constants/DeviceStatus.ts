export const DeviceStatus = ["NORMAL", "OUTAGE", "PENDING_REUSE", "FAULT"] as const;
export type DeviceStatus = (typeof DeviceStatus)[number];

export const DeviceStatusText: Record<DeviceStatus, string> = {
  NORMAL: "正常",
  OUTAGE: "停用中",
  PENDING_REUSE: "待复役",
  FAULT: "待修"
};

export const DeviceStatusOptions = DeviceStatus.map((value) => ({ value, label: DeviceStatusText[value] }));
