export const HazardSeverity = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] as const;
export type HazardSeverity = (typeof HazardSeverity)[number];
