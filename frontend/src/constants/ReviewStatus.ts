// 停用变更后，引用停用设备的巡检结果与隐患整改单 -> 作废待复核
export const ReviewStatus = ["ACTIVE", "VOID_PENDING", "RECONFIRMED", "REJECTED"] as const;
export type ReviewStatus = (typeof ReviewStatus)[number];
export const ReviewStatusText: Record<ReviewStatus, string> = {
  ACTIVE: "有效",
  VOID_PENDING: "作废待复核",
  RECONFIRMED: "复核通过",
  REJECTED: "维持作废"
};
