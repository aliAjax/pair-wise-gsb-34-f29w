import { ReviewStatusText } from "../../constants/ReviewStatus";
import { StatusBadge } from "./StatusBadge";

/**
 * 作废待复核标记：停用时段变更后，
 * 引用停用设备的巡检结果 / 隐患整改单统一展示此标记。
 */
export function ReviewFlag({
  reviewStatus,
  windowId
}: {
  reviewStatus: string;
  windowId?: number | null;
}) {
  if (reviewStatus === "ACTIVE") return null;
  const label =
    ReviewStatusText[reviewStatus as keyof typeof ReviewStatusText] ??
    reviewStatus;
  return (
    <span
      className={
        "review-flag " + reviewStatus.toLowerCase().replace(/_/g, "-")
      }
      title={windowId ? `由停用时段 #${windowId} 变更触发` : "待复核"}
    >
      <StatusBadge value={reviewStatus} group="ReviewStatus" />
      <em>{label}</em>
    </span>
  );
}
