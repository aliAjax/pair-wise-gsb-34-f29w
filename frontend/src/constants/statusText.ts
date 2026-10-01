import { DeviceTypeText } from "./DeviceType";
import { DeviceStatusText } from "./DeviceStatus";
import { InspectionStatusText } from "./InspectionStatus";
import { HazardSeverityText } from "./HazardSeverity";
import { OutageStatusText } from "./OutageStatus";

// 多页面共用的状态文案总表；utils/formatters 也依赖这里
export const STATUS_TEXT = {
  DeviceType: DeviceTypeText,
  DeviceStatus: DeviceStatusText,
  InspectionStatus: InspectionStatusText,
  HazardSeverity: HazardSeverityText,
  OutageStatus: OutageStatusText
};
