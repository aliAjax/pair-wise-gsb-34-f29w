// 巡检排期（任务-设备关系）状态。ORIGINAL 原关系始终保留。
export const AssignmentStatus = [
  "ORIGINAL",
  "BACKUP",
  "PENDING_RECHECK",
  "RESCHEDULED",
  "DONE"
] as const;
export type AssignmentStatus = (typeof AssignmentStatus)[number];
export const AssignmentStatusText: Record<AssignmentStatus, string> = {
  ORIGINAL: "原计划",
  BACKUP: "备用设备",
  PENDING_RECHECK: "待补检",
  RESCHEDULED: "已补排",
  DONE: "已完成"
};
