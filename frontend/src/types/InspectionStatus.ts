export const InspectionStatus = [
  "PLANNED",
  "IN_PROGRESS",
  "SUBMITTED",
  "REVIEWED",
  "OVERDUE",
  "PENDING_MAKEUP"
] as const;
export type InspectionStatus = (typeof InspectionStatus)[number];
