import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

export function EmptyState({ title = "暂无数据", hint }: { title?: string; hint?: string }) {
  return (
    <Box
      sx={{
        border: "1px dashed #b8b09f",
        borderRadius: 2,
        p: 4,
        textAlign: "center",
        color: "text.secondary"
      }}
    >
      <Typography variant="body1" sx={{ fontWeight: 700 }}>
        {title}
      </Typography>
      {hint ? (
        <Typography variant="caption" sx={{ mt: 1, display: "block" }}>
          {hint}
        </Typography>
      ) : null}
    </Box>
  );
}
