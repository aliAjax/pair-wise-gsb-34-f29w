import Box from "@mui/material/Box";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import { useChecklistProgress } from "../../hooks/useChecklistProgress";
import type { InspectionResult } from "../../types/InspectionResult";

// 任务页共用：检查项完成进度 + 作废待复核数量
export function ChecklistPanel({
  results,
  title = "检查项进度"
}: {
  results: InspectionResult[];
  title?: string;
}) {
  const progress = useChecklistProgress(results);
  return (
    <Box sx={{ border: "1px solid #e0dccf", borderRadius: 2, p: 2, bgcolor: "#fbfaf4" }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
        {title}
      </Typography>
      <LinearProgress
        variant="determinate"
        value={progress.percent}
        sx={{ height: 8, borderRadius: 4, bgcolor: "#ece7dd", "& .MuiLinearProgress-bar": { bgcolor: "#274335" } }}
      />
      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: "block" }}>
        有效 {progress.done}/{progress.total} 项
        {progress.voided > 0 ? `，另有 ${progress.voided} 项因停用变化作废待复核` : ""}
      </Typography>
    </Box>
  );
}
