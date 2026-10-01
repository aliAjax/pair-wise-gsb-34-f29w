export const HazardSeverity = ["LOW","MEDIUM","HIGH","CRITICAL"] as const;
export type HazardSeverity = (typeof HazardSeverity)[number];
export const HazardSeverityText: Record<HazardSeverity, string> = {
  LOW: "低",
  MEDIUM: "中",
  HIGH: "高",
  CRITICAL: "紧急"
};
