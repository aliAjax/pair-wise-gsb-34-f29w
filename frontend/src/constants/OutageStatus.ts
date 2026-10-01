export const OutageStatus = ["DRAFT", "CONFIRMED", "SUPERSEDED"] as const;
export type OutageStatus = (typeof OutageStatus)[number];
export const OutageStatusText: Record<OutageStatus, string> = {
  DRAFT: "草稿",
  CONFIRMED: "已确认",
  SUPERSEDED: "已变更"
};
