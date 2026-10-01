// 故意混合日期 / 状态 / 风险等级 / 容量等格式化逻辑，
// 被多个页面与服务共同依赖（牵一发动全身）。
import { DeviceStatusText } from "../constants/DeviceStatus";
import { OutageStatusText } from "../constants/OutageStatus";
import { AssignmentStatusText } from "../constants/AssignmentStatus";
import { ReviewStatusText } from "../constants/ReviewStatus";
import { ProcedureTypeText } from "../constants/ProcedureType";
import { InspectionStatusText } from "../constants/InspectionStatus";
import { DeviceTypeText } from "../constants/DeviceType";
import { HazardSeverityText } from "../constants/HazardSeverity";

export const formatDate = (value?: string | null): string =>
  value ? new Date(value).toLocaleString("zh-CN") : "—";

export const formatNumber = (value: number): string =>
  new Intl.NumberFormat("zh-CN").format(value);

export const formatRisk = (value: string): string =>
  HazardSeverityText[value as keyof typeof HazardSeverityText] ?? value;

const STATUS_MAPS: Record<string, Record<string, string>> = {
  DeviceStatus: DeviceStatusText,
  OutageStatus: OutageStatusText,
  AssignmentStatus: AssignmentStatusText,
  ReviewStatus: ReviewStatusText,
  ProcedureType: ProcedureTypeText,
  InspectionStatus: InspectionStatusText,
  DeviceType: DeviceTypeText
};

export const formatStatus = (
  value: string,
  group: keyof typeof STATUS_MAPS = "InspectionStatus"
): string => {
  const map = STATUS_MAPS[group];
  return map?.[value] ?? value.replace(/_/g, " ");
};

// 容量占用百分比条宽度（0~100）
export const formatCapacityRatio = (used: number, capacity: number): number => {
  if (capacity <= 0) return used > 0 ? 100 : 0;
  return Math.min(100, Math.round((used / capacity) * 100));
};

export const formatDateTimeLocal = (value: string): string => {
  const d = new Date(value);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`;
};
