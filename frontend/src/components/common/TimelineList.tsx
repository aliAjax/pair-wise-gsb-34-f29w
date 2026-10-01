import Box from "@mui/material/Box";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";

export interface TimelineEntry {
  id: string | number;
  title: string;
  time?: string | null;
  tone?: string;
}

// 任务页与隐患页共用的时间轴列表（改派、排队、作废、复役等事件）
export function TimelineList({
  title,
  entries = []
}: {
  title: string;
  entries?: TimelineEntry[];
}) {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
        {title}
      </Typography>
      {entries.length === 0 ? (
        <Typography variant="caption" color="text.secondary">
          暂无联动事件
        </Typography>
      ) : (
        <List dense disablePadding sx={{ position: "relative" }}>
          {entries.map((entry, index) => (
            <ListItem
              key={entry.id}
              disableGutters
              sx={{
                pl: 2,
                borderLeft: "2px solid #d39b46",
                position: "relative",
                "&::before": {
                  content: '""',
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  bgcolor: entry.tone ?? "#d39b46",
                  position: "absolute",
                  left: -5
                }
              }}
            >
              <ListItemText
                primary={entry.title}
                secondary={entry.time}
                primaryTypographyProps={{ variant: "body2", fontWeight: index === 0 ? 700 : 400 }}
                secondaryTypographyProps={{ variant: "caption" }}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
}
