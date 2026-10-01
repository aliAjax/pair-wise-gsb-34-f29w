import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";

export function PageHeader({
  title,
  eyebrow = "fire-inspect",
  actions
}: {
  title: string;
  eyebrow?: string;
  actions?: ReactNode;
}) {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 3,
        borderRadius: 3,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 2,
        flexWrap: "wrap",
        bgcolor: "#fbfaf4",
        border: "1px solid #e0dccf"
      }}
    >
      <div>
        <Typography variant="caption" sx={{ color: "#7d4d18", fontWeight: 800, letterSpacing: 1.5 }}>
          {eyebrow}
        </Typography>
        <Typography variant="h4" sx={{ fontWeight: 800 }}>
          {title}
        </Typography>
      </div>
      {actions ? <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>{actions}</div> : null}
    </Paper>
  );
}
