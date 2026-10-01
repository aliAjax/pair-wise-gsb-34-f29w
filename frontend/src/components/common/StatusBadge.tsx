import Chip from "@mui/material/Chip";
import { formatStatus } from "../../utils/formatters";
import type { STATUS_TEXT } from "../../constants/statusText";

type StatusKind = keyof typeof STATUS_TEXT;

const COLOR_MAP: Record<string, { bg: string; color: string }> = {
  NORMAL: { bg: "#e4efe4", color: "#244b31" },
  CONFIRMED: { bg: "#e4efe4", color: "#244b31" },
  REVIEWED: { bg: "#e4efe4", color: "#244b31" },
  ACTIVE: { bg: "#e4efe4", color: "#244b31" },
  VERIFIED: { bg: "#e4efe4", color: "#244b31" },
  PLANNED: { bg: "#e7eef7", color: "#27435f" },
  IN_PROGRESS: { bg: "#e7eef7", color: "#27435f" },
  ASSIGNED: { bg: "#e7eef7", color: "#27435f" },
  SUBMITTED: { bg: "#fdf3df", color: "#7d4d18" },
  RECTIFIED: { bg: "#fdf3df", color: "#7d4d18" },
  OUTAGE: { bg: "#fbe4e4", color: "#8a2b2b" },
  OVERDUE: { bg: "#fbe4e4", color: "#8a2b2b" },
  VOID_PENDING_REVIEW: { bg: "#fbe4e4", color: "#8a2b2b" },
  VOID_CONFIRMED: { bg: "#ece7dd", color: "#5b574c" },
  SUPERSEDED: { bg: "#ece7dd", color: "#5b574c" },
  CANCELLED: { bg: "#ece7dd", color: "#5b574c" },
  PENDING_REUSE: { bg: "#fdf3df", color: "#7d4d18" },
  PENDING_MAKEUP: { bg: "#f6e7c9", color: "#8a5a12" },
  DRAFT: { bg: "#fdf3df", color: "#7d4d18" },
  PENDING: { bg: "#fbe4e4", color: "#8a2b2b" },
  FAULT: { bg: "#fbe4e4", color: "#8a2b2b" },
  OPEN: { bg: "#fdf3df", color: "#7d4d18" }
};

// 多页面共用：设备/任务/结果/停用状态徽标。文案来自 constants/statusText
export function StatusBadge({ value, kind }: { value: string; kind?: StatusKind }) {
  const label = kind ? formatStatus(kind, value) : value.replace(/_/g, " ");
  const tone = COLOR_MAP[value] ?? { bg: "#ece7dd", color: "#5b574c" };
  return (
    <Chip
      size="small"
      label={label}
      sx={{ bgcolor: tone.bg, color: tone.color, fontWeight: 700, borderRadius: "999px" }}
    />
  );
}
