// 复役前必须补齐的手续
export const ProcedureType = ["MAINTENANCE_REPORT", "ACCEPTANCE_CHECK", "SAFETY_SIGN_OFF"] as const;
export type ProcedureType = (typeof ProcedureType)[number];
export const ProcedureTypeText: Record<ProcedureType, string> = {
  MAINTENANCE_REPORT: "保养完工报告",
  ACCEPTANCE_CHECK: "验收检测",
  SAFETY_SIGN_OFF: "安全责任人签收"
};

// 写入阶段（断点续跑）
export const WriteStage = [
  "PERSIST_WINDOW",
  "HOLD_CAPACITY",
  "REALLOCATE_TASKS",
  "MARK_DEVICE_OUTAGE",
  "COMPLETED"
] as const;
export type WriteStage = (typeof WriteStage)[number];
export const WriteStageText: Record<WriteStage, string> = {
  PERSIST_WINDOW: "停用时段落库",
  HOLD_CAPACITY: "占用备用容量",
  REALLOCATE_TASKS: "巡检任务重排",
  MARK_DEVICE_OUTAGE: "设备置为停用",
  COMPLETED: "确认完成"
};
