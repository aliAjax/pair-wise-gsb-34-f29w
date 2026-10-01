import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";

// 报表页共享图表面板（内部条形图由各页自行组装）
export function ChartPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 3, height: "100%" }}>
      <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>
        {title}
      </Typography>
      {children}
    </Paper>
  );
}
