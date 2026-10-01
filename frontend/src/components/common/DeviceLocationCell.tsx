import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import type { Building } from "../../types/Building";
import type { FireDevice } from "../../types/FireDevice";
import { formatStatus } from "../../utils/formatters";
import { StatusBadge } from "./StatusBadge";

// 设备台账页共用：楼层 + 位置 + 所属楼栋
export function DeviceLocationCell({
  device,
  building
}: {
  device: FireDevice;
  building?: Building;
}) {
  return (
    <Box>
      <Typography variant="body2" sx={{ fontWeight: 700 }}>
        {device.floor} · {device.location_desc}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {building ? `${building.name}（${building.campus}）` : `楼栋 #${device.building_id}`} ·{" "}
        {formatStatus("DeviceType", device.device_type)}
      </Typography>
      <Box sx={{ mt: 0.5 }}>
        <StatusBadge value={device.status} kind="DeviceStatus" />
      </Box>
    </Box>
  );
}
