import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";

export interface FilterOption {
  value: string;
  label: string;
}

// 设备台账 / 任务 / 隐患页共用筛选条
export function FilterBar({
  filters
}: {
  filters: {
    label: string;
    value: string;
    options: FilterOption[];
    onChange: (value: string) => void;
  }[];
}) {
  return (
    <Box sx={{ display: "flex", gap: 1.5, flexWrap: "wrap" }}>
      {filters.map((filter) => (
        <TextField
          key={filter.label}
          select
          size="small"
          label={filter.label}
          value={filter.value}
          onChange={(event) => filter.onChange(event.target.value)}
          sx={{ minWidth: 160, bgcolor: "#fff", borderRadius: 1 }}
        >
          <MenuItem value="">全部</MenuItem>
          {filter.options.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </TextField>
      ))}
    </Box>
  );
}
