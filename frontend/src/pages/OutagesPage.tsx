import { useEffect, useMemo, useState } from "react";
import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControlLabel from "@mui/material/FormControlLabel";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

import {
  cancelOutage,
  changeOutageWindow,
  resumeOutageBatch,
  reviewOutageDraft,
  submitOutages
} from "../api/DeviceOutage";
import { DEMO_USERS, RoleText } from "../constants/roles";
import { PageHeader } from "../components/common/PageHeader";
import { StatusBadge } from "../components/common/StatusBadge";
import { TimelineList, type TimelineEntry } from "../components/common/TimelineList";
import { EmptyState } from "../components/common/EmptyState";
import { useToast } from "../components/common/Toast";
import { fetchFireDevices } from "../stores/FireDeviceStore";
import { fetchOutageBatches } from "../stores/DeviceOutageStore";
import { useAppDispatch, useAppSelector } from "../stores/hooks";
import { formatShortDate } from "../utils/formatters";
import type { DeviceOutage } from "../types/DeviceOutage";

// 默认停用窗口：后天 09:00-17:00（与种子巡检计划重叠）
function defaultWindow(offsetDay = 2) {
  const base = new Date();
  base.setDate(base.getDate() + offsetDay);
  base.setHours(9, 0, 0, 0);
  const end = new Date(base);
  end.setHours(17, 0, 0, 0);
  const fmt = (d: Date) => {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };
  return { start: fmt(base), end: fmt(end) };
}

function outageEvents(item: DeviceOutage): TimelineEntry[] {
  const entries: TimelineEntry[] = [];
  item.reroute?.rerouted.forEach((r, index) =>
    entries.push({
      id: `r-${index}`,
      title: `任务 #${r.task_id} 改派到备用设备 #${r.backup_device_id}（原任务关系保留）`,
      tone: "#274335"
    })
  );
  item.reroute?.queued.forEach((q, index) =>
    entries.push({
      id: `q-${index}`,
      title: `任务 #${q.task_id} 备用容量不足，排队待补检`,
      tone: "#8a5a12"
    })
  );
  if ((item.cascade?.voided_count ?? 0) > 0) {
    entries.push({
      id: "void",
      title: `引用该设备的 ${item.cascade?.voided_result_ids.length ?? 0} 条结果、${item.cascade?.voided_ticket_ids.length ?? 0} 张隐患单作废待复核`,
      tone: "#8a2b2b"
    });
  }
  if (item.status === "DRAFT" && item.occupied_count > 0) {
    entries.unshift({
      id: "conflict",
      title: `与 ${item.occupied_count} 个已确认停用名额冲突，已保留草稿`,
      tone: "#7d4d18"
    });
  }
  return entries;
}

export function OutagesPage() {
  const dispatch = useAppDispatch();
  const { notify, notifyError } = useToast();
  const devices = useAppSelector((state) => state.fireDevice.rows);
  const batches = useAppSelector((state) => state.deviceOutage.batches);
  const actorId = useAppSelector((state) => state.session.actorId);
  const actor = DEMO_USERS.find((user) => user.id === actorId) ?? DEMO_USERS[2];
  // 停用写入仅维保商/主管；审计员只读
  const canManage = actor.role === "MAINTAINER" || actor.role === "SUPERVISOR";

  const [open, setOpen] = useState(false);
  const [selectedCodes, setSelectedCodes] = useState<string[]>([]);
  const win = useMemo(() => defaultWindow(2), []);
  const [startAt, setStartAt] = useState(win.start);
  const [endAt, setEndAt] = useState(win.end);
  const [reason, setReason] = useState("例行停机保养");
  const [simulateFail, setSimulateFail] = useState(true);
  const [changing, setChanging] = useState<DeviceOutage | null>(null);
  const [changeStart, setChangeStart] = useState("");
  const [changeEnd, setChangeEnd] = useState("");

  const reload = () => {
    void dispatch(fetchFireDevices());
    void dispatch(fetchOutageBatches());
  };

  useEffect(() => {
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatch]);

  const toggleDevice = (code: string) => {
    setSelectedCodes((prev) => (prev.includes(code) ? prev.filter((value) => value !== code) : [...prev, code]));
  };

  const submit = async () => {
    if (selectedCodes.length === 0) {
      notify("请至少选择一台设备", "warning");
      return;
    }
    try {
      const batch = await submitOutages({
        items: selectedCodes.map((code) => ({ device_code: code, start_at: startAt, end_at: endAt, reason })),
        note: `${actor.name}（${RoleText[actor.role]}）提交`,
        fail_device_codes: simulateFail ? selectedCodes.slice(-1) : []
      });
      const draftCount = batch.items.filter((item) => item.status === "DRAFT" && item.occupied_count > 0).length;
      const pendingCount = batch.items.filter((item) => item.status === "PENDING").length;
      notify(
        `提交完成：冲突草稿 ${draftCount} 条${pendingCount ? `，${pendingCount} 台写入失败待续传` : ""}`,
        pendingCount || draftCount ? "warning" : "success"
      );
      setOpen(false);
      setSelectedCodes([]);
      reload();
    } catch (error) {
      notifyError(error);
    }
  };

  const resume = async (batchId: number) => {
    try {
      const batch = await resumeOutageBatch(batchId);
      const queued = batch.items.reduce(
        (sum, item) => sum + (item.reroute?.queued.length ?? 0),
        0
      );
      notify(`续传成功，新增排队待补检 ${queued} 单，已占名额未重复`, "success");
      reload();
    } catch (error) {
      notifyError(error);
    }
  };

  const reviewDraft = async (item: DeviceOutage, action: "CONFIRM" | "CANCEL") => {
    try {
      const result = await reviewOutageDraft(item.id, action);
      if (action === "CONFIRM" && result.status === "DRAFT") {
        notify(`仍有 ${result.occupied_count} 个名额被占用，继续保留草稿`, "warning");
      } else {
        notify(action === "CONFIRM" ? "已确认占用名额" : "草稿已放弃", "success");
      }
      reload();
    } catch (error) {
      notifyError(error);
    }
  };

  const openChange = (item: DeviceOutage) => {
    setChanging(item);
    setChangeStart(item.start_at.slice(0, 16));
    setChangeEnd(item.end_at.slice(0, 16));
  };

  const saveChange = async () => {
    if (!changing) return;
    try {
      const result = await changeOutageWindow(changing.id, {
        start_at: changeStart,
        end_at: changeEnd,
        reason: `${reason}（改期）`
      });
      notify(
        `时段已变化：旧版本作废，${result.cascade?.voided_count ?? 0} 条记录作废待复核`,
        "warning"
      );
      setChanging(null);
      reload();
    } catch (error) {
      notifyError(error);
    }
  };

  const cancel = async (item: DeviceOutage) => {
    try {
      const result = await cancelOutage(item.id);
      notify(`已撤销停用，${result.outage.cascade?.voided_count ?? 0} 条记录作废待复核`, "warning");
      reload();
    } catch (error) {
      notifyError(error);
    }
  };

  return (
    <Box sx={{ display: "grid", gap: 3 }}>
      <PageHeader
        title="停机保养排期"
        actions={canManage ? (
          <Button variant="contained" onClick={() => setOpen(true)} sx={{ bgcolor: "#274335" }}>
            提交停用时段
          </Button>
        ) : undefined}
      />

      <Paper variant="outlined" sx={{ p: 2, borderRadius: 3, bgcolor: "#fbfaf4" }}>
        <Typography variant="body2" color="text.secondary">
          规则：同段巡检优先改用同栋同类型备用设备（每台窗口容量 1 槽），容量不足排队转
          <Chip size="small" label="待补检" sx={{ mx: 0.5 }} />；
          两个负责人确认重叠时段时，后到者看到占用数量并保留草稿；写入失败可续传，已占名额不重复不丢失；停用时段一变，引用结果/隐患单作废待复核；复役前手续没齐不能回到正常。
        </Typography>
      </Paper>

      {batches.length === 0 ? (
        <EmptyState title="还没有停用批次" hint="点击右上角“提交停用时段”开始排期" />
      ) : (
        batches.map((batch) => (
          <Accordion key={batch.id} defaultExpanded disableGutters sx={{ borderRadius: 2, border: "1px solid #e0dccf" }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Stack direction="row" spacing={1.5} alignItems="center" sx={{ width: "100%" }}>
                <Typography sx={{ fontWeight: 800 }}>批次 #{batch.id}</Typography>
                <StatusBadge value={batch.status} kind="OutageStatus" />
                <Typography variant="caption" color="text.secondary">
                  {batch.note} · {batch.items.length} 台设备
                  {batch.fail_device_codes.length > 0 ? ` · 模拟失败 ${batch.fail_device_codes.join("、")}` : ""}
                </Typography>
                {batch.items.some((item) => item.status === "PENDING") && canManage ? (
                  <Button
                    size="small"
                    variant="outlined"
                    color="warning"
                    onClick={(event) => {
                      event.stopPropagation();
                      void resume(batch.id);
                    }}
                  >
                    续传未生效设备
                  </Button>
                ) : null}
              </Stack>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {batch.items.map((item) => {
                  const device = devices.find((row) => row.id === item.device_id);
                  return (
                    <Grid xs={12} md={6} key={item.id}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Box>
                            <Typography sx={{ fontWeight: 800 }}>
                              {device?.device_code ?? `设备#${item.device_id}`}
                              <Typography component="span" variant="caption" sx={{ ml: 1 }} color="text.secondary">
                                v{item.version}
                              </Typography>
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatShortDate(item.start_at)} ~ {formatShortDate(item.end_at)} · {item.reason}
                            </Typography>
                          </Box>
                          <StatusBadge value={item.status} kind="OutageStatus" />
                        </Stack>

                        <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: "wrap" }}>
                          <Chip size="small" label={`受影响 ${item.reroute?.affected_slot_count ?? 0}`} />
                          <Chip size="small" color="success" label={`改派 ${item.reroute?.rerouted.length ?? 0}`} />
                          <Chip size="small" color="warning" label={`待补检 ${item.reroute?.queued.length ?? 0}`} />
                          {item.status === "DRAFT" && item.occupied_count > 0 ? (
                            <Chip size="small" color="error" label={`占用数量 ${item.occupied_count}`} />
                          ) : null}
                        </Stack>

                        <Box sx={{ mt: 1.5 }}>
                          <TimelineList title="联动事件" entries={outageEvents(item)} />
                        </Box>

                        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                          {item.status === "DRAFT" && item.occupied_count > 0 && canManage ? (
                            <>
                              <Button size="small" variant="contained" onClick={() => void reviewDraft(item, "CONFIRM")}>
                                仍要确认
                              </Button>
                              <Button size="small" color="inherit" onClick={() => void reviewDraft(item, "CANCEL")}>
                                放弃草稿
                              </Button>
                            </>
                          ) : null}
                          {item.status === "CONFIRMED" && canManage ? (
                            <>
                              <Button size="small" onClick={() => openChange(item)}>变更时段</Button>
                              <Button size="small" color="error" onClick={() => void cancel(item)}>撤销停用</Button>
                            </>
                          ) : null}
                        </Stack>
                      </Paper>
                    </Grid>
                  );
                })}
              </Grid>
            </AccordionDetails>
          </Accordion>
        ))
      )}

      {/* 提交对话框 */}
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>提交消防设备停用时段</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              type="datetime-local"
              label="停用开始"
              value={startAt}
              onChange={(event) => setStartAt(event.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              type="datetime-local"
              label="停用结束"
              value={endAt}
              onChange={(event) => setEndAt(event.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField label="停用原因" value={reason} onChange={(event) => setReason(event.target.value)} />
            <FormControlLabel
              control={<Checkbox checked={simulateFail} onChange={(event) => setSimulateFail(event.target.checked)} />}
              label="模拟最后一台设备首次写入失败（用于演示恢复续传）"
            />
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">选</TableCell>
                  <TableCell>编号</TableCell>
                  <TableCell>楼栋</TableCell>
                  <TableCell>类型</TableCell>
                  <TableCell>状态</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {devices.map((device) => (
                  <TableRow key={device.id} hover selected={selectedCodes.includes(device.device_code)}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedCodes.includes(device.device_code)}
                        onChange={() => toggleDevice(device.device_code)}
                      />
                    </TableCell>
                    <TableCell>{device.device_code}</TableCell>
                    <TableCell>#{device.building_id}</TableCell>
                    <TableCell>{device.device_type}</TableCell>
                    <TableCell><StatusBadge value={device.status} kind="DeviceStatus" /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>取消</Button>
          <Button variant="contained" onClick={void submit} sx={{ bgcolor: "#274335" }}>提交</Button>
        </DialogActions>
      </Dialog>

      {/* 变更时段对话框 */}
      <Dialog open={changing !== null} onClose={() => setChanging(null)} fullWidth maxWidth="xs">
        <DialogTitle>变更停用时段 #{changing?.id}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              type="datetime-local"
              label="新开始"
              value={changeStart}
              onChange={(event) => setChangeStart(event.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              type="datetime-local"
              label="新结束"
              value={changeEnd}
              onChange={(event) => setChangeEnd(event.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <Typography variant="caption" color="error">
              保存后旧时段标记为已作废，引用该设备的巡检结果与隐患整改单作废待复核，并按新窗口重算改派。
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setChanging(null)}>取消</Button>
          <Button variant="contained" onClick={void saveChange} color="warning">保存变更</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
