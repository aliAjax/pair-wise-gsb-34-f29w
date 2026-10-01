export const OutageStatus = ["DRAFT", "CONFIRMED", "SUPERSEDED", "CANCELLED", "PENDING"] as const;
export type OutageStatus = (typeof OutageStatus)[number];

export const OutageStatusText: Record<OutageStatus, string> = {
  DRAFT: "冲突草稿",
  CONFIRMED: "已确认",
  SUPERSEDED: "已作废",
  CANCELLED: "已撤销",
  PENDING: "待续传"
};

export const OutageBatchStatus = ["PARTIAL_FAILED", "COMPLETED", "RESUMED"] as const;
export type OutageBatchStatus = (typeof OutageBatchStatus)[number];
export const OutageBatchStatusText: Record<OutageBatchStatus, string> = {
  PARTIAL_FAILED: "部分失败",
  COMPLETED: "已完成",
  RESUMED: "已续传"
};

// 与后端 BACKUP_SLOT_CAPACITY 保持一致
export const BACKUP_SLOT_CAPACITY = 1;
