import { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControlLabel from "@mui/material/FormControlLabel";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";

import { addReusePaperwork, reactivateFireDevice } from "../api/FireDevice";
import { DEMO_USERS } from "../constants/roles";
import { DeviceStatusOptions } from "../constants/DeviceStatus";
import { DeviceTypeOptions, DeviceTypeText } from "../constants/DeviceType";
import { PageHeader } from "../components/common/PageHeader";
import { StatusBadge } from "../components/common/StatusBadge";
import { DeviceLocationCell } from "../components/common/DeviceLocationCell";
import { FilterBar } from "../components/common/FilterBar";
import { EmptyState } from "../components/common/EmptyState";
import { useToast } from "../components/common/Toast";
import { fetchBuildings } from "../stores/BuildingStore";
import { fetchFireDevices } from "../stores/FireDeviceStore";
import { useAppDispatch, useAppSelector } from "../stores/hooks";
import { formatDate } from "../utils/formatters";
import type { FireDevice } from "../types/FireDevice";

// 与后端 REUSE_PAPERWORK_ITEMS 对齐
const PAPERWORK = [
  { value: "MAINTENANCE_REPORT", label: "维保报告" },
  { value: "SAFETY_CHECK", label: "安全检测" },
  { value: "MANAGER_SIGN_OFF", label: "主管签字" }
];

export function DevicesPage() {
  const dispatch = useAppDispatch();
  const { notify, notifyError } = useToast();
  const devices = useAppSelector((state) => state.fireDevice.rows);
  const buildings = useAppSelector((state) => state.building.rows);
  const actorId = useAppSelector((state) => state.session.actorId);
  const actor = DEMO_USERS.find((user) => user.id === actorId) ?? DEMO_USERS[2];
  // 复役相关按钮仅维保商/主管可见，巡检员只读
  const canReactivate = actor.role === "MAINTAINER" || actor.role === "SUPERVISOR";
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [paperworkDevice, setPaperworkDevice] = useState<FireDevice | null>(null);
  const [checked, setChecked] = useState<string[]>([]);

  useEffect(() => {
    void dispatch(fetchBuildings());
    void dispatch(fetchFireDevices({ status: statusFilter, device_type: typeFilter }));
  }, [dispatch, statusFilter, typeFilter]);

  const openPaperwork = (device: FireDevice) => {
    setPaperworkDevice(device);
    setChecked(device.reuse_paperwork);
  };

  const savePaperwork = async () => {
    if (!paperworkDevice) return;
    try {
      await addReusePaperwork(paperworkDevice.id, checked);
      notify("复役手续已登记", "success");
      setPaperworkDevice(null);
      void dispatch(fetchFireDevices({ status: statusFilter, device_type: typeFilter }));
    } catch (error) {
      notifyError(error);
    }
  };

  const reactivate = async (device: FireDevice) => {
    try {
      const updated = await reactivateFireDevice(device.id);
      notify(`设备 ${updated.device_code} 已恢复正常`, "success");
      void dispatch(fetchFireDevices({ status: statusFilter, device_type: typeFilter }));
    } catch (error) {
      // 手续没补齐：后端已把设备置为待复役
      notifyError(error);
      void dispatch(fetchFireDevices({ status: statusFilter, device_type: typeFilter }));
    }
  };

  return (
    <Box sx={{ display: "grid", gap: 3 }}>
      <PageHeader title="消防设备台账" />

      <FilterBar
        filters={[
          { label: "设备状态", value: statusFilter, options: DeviceStatusOptions, onChange: setStatusFilter },
          { label: "设备类型", value: typeFilter, options: DeviceTypeOptions, onChange: setTypeFilter }
        ]}
      />

      <Paper variant="outlined" sx={{ borderRadius: 3, overflow: "hidden" }}>
        {devices.length === 0 ? (
          <Box sx={{ p: 3 }}>
            <EmptyState title="没有符合筛选条件的设备" />
          </Box>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>设备编号</TableCell>
                <TableCell>位置 / 楼栋</TableCell>
                <TableCell>下次维保</TableCell>
                <TableCell>复役手续</TableCell>
                <TableCell align="right">操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {devices.map((device) => {
                const building = buildings.find((row) => row.id === device.building_id);
                const missing = PAPERWORK.filter((item) => !device.reuse_paperwork.includes(item.value));
                return (
                  <TableRow key={device.id} hover>
                    <TableCell>
                      <Typography sx={{ fontWeight: 700 }}>{device.device_code}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {DeviceTypeText[device.device_type as keyof typeof DeviceTypeText] ?? device.device_type}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <DeviceLocationCell device={device} building={building} />
                    </TableCell>
                    <TableCell>{formatDate(device.next_maintenance_at)}</TableCell>
                    <TableCell>
                      {device.status === "NORMAL" ? (
                        <Typography variant="caption" color="text.secondary">—</Typography>
                      ) : missing.length === 0 ? (
                        <Typography variant="caption" sx={{ color: "#244b31", fontWeight: 700 }}>
                          手续齐全，可复役
                        </Typography>
                      ) : (
                        <Typography variant="caption" color="#8a5a12">
                          缺：{missing.map((item) => item.label).join("、")}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        {device.status === "OUTAGE" || device.status === "PENDING_REUSE" ? (
                          canReactivate ? (
                            <>
                              <Button size="small" onClick={() => openPaperwork(device)}>补手续</Button>
                              <Button
                                size="small"
                                variant="contained"
                                color={device.status === "PENDING_REUSE" ? "warning" : "primary"}
                                onClick={() => void reactivate(device)}
                              >
                                申请复役
                              </Button>
                            </>
                          ) : (
                            <Typography variant="caption" color="text.secondary">需维保商/主管处理复役</Typography>
                          )
                        ) : (
                          <StatusBadge value={device.status} kind="DeviceStatus" />
                        )}
                      </Stack>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </Paper>

      <Dialog open={paperworkDevice !== null} onClose={() => setPaperworkDevice(null)} fullWidth maxWidth="xs">
        <DialogTitle>复役手续 · {paperworkDevice?.device_code}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            手续没补齐的设备不能回到正常，将停留在“待复役”。
          </Typography>
          {PAPERWORK.map((item) => (
            <FormControlLabel
              key={item.value}
              control={
                <Checkbox
                  checked={checked.includes(item.value)}
                  onChange={(event) =>
                    setChecked((prev) =>
                      event.target.checked ? [...prev, item.value] : prev.filter((value) => value !== item.value)
                    )
                  }
                />
              }
              label={item.label}
            />
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPaperworkDevice(null)}>取消</Button>
          <Button variant="contained" onClick={void savePaperwork}>保存手续</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
