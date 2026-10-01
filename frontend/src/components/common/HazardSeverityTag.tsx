import Chip from "@mui/material/Chip";
import { formatRisk } from "../../utils/formatters";

const TONE: Record<string, { bg: string; color: string }> = {
  LOW: { bg: "#e4efe4", color: "#244b31" },
  MEDIUM: { bg: "#fdf3df", color: "#7d4d18" },
  HIGH: { bg: "#f8e2c6", color: "#9a5410" },
  CRITICAL: { bg: "#fbe4e4", color: "#8a2b2b" }
};

// 隐患分级标签：总览页与隐患页共用
export function HazardSeverityTag({ value }: { value: string }) {
  const tone = TONE[value] ?? { bg: "#ece7dd", color: "#5b574c" };
  return (
    <Chip
      size="small"
      label={formatRisk(value)}
      sx={{ bgcolor: tone.bg, color: tone.color, fontWeight: 800 }}
    />
  );
}
