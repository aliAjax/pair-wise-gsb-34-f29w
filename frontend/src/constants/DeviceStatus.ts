export const DeviceStatus = ["NORMAL", "OUT_OF_SERVICE", "RESTORED"] as const;
export type DeviceStatus = (typeof DeviceStatus)[number];
export const DeviceStatusText: Record<DeviceStatus, string> = {
  NORMAL: "正常",
  OUT_OF_SERVICE: "停用",
  RESTORED: "已复役"
};
