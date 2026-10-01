import { useEffect, useMemo, useState } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";

import { reviewVoidedResult } from "../api/InspectionResult";
import { DEMO_USERS } from "../constants/roles";
import { InspectionStatusOptions } from "../constants/InspectionStatus";
import { ChecklistPanel } from "../components/common/ChecklistPanel";
import { PageHeader } from "../components/common/PageHeader";
import { StatusBadge } from "../components/common/StatusBadge";
import { FilterBar } from "../components/common/FilterBar";
import { EmptyState } from "../components/common/EmptyState";
import { TimelineList, type TimelineEntry } from "../components/common/TimelineList";
import { useToast } from "../components/common/Toast";
import { fetchFireDevices } from "../stores/FireDeviceStore";
import { fetchInspectionResults } from "../stores/InspectionResultStore";
import { fetchInspectionTasks } from "../stores/InspectionTaskStore";
import { fetchOutageBatches } from "../stores/DeviceOutageStore";
import { useAppDispatch, useAppSelector } from "../stores/hooks";
import { formatShortDate, formatStatus } from "../utils/formatters";
import type { DeviceOutage } from "../types/DeviceOutage";

export function TasksPage() {
  const dispatch = useAppDispatch();
  const { notify, notifyError } = useToast();
  const tasks = useAppSelector((state) => state.inspectionTask.rows);
  const results = useAppSelector((state) => state.inspectionResult.rows);
  const devices = useAppSelector((state) => state.fireDevice.rows);
  const batches = useAppSelector((state) => state.deviceOutage.batches);
  const actorId = useAppSelector((state) => state.session.actorId);
  const actor = DEMO_USERS.find((user) => user.id === actorId) ?? DEMO_USERS[2];
  // 作废复核仅主管/审计可操作
  const canReview = actor.role === "SUPERVISOR" || actor.role === "AUDITOR";
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);

  useEffect(() => {
    void dispatch(fetchFireDevices());
    void dispatch(fetchInspectionResults());
    void dispatch(fetchOutageBatches());
    void dispatch(fetchInspectionTasks({ status: statusFilter }));
  }, [dispatch, statusFilter]);

  // 所有停用条目（含批次内），用于定位任务被改派/排队事件
  const outageItems = useMemo<DeviceOutage[]>(
    () => batches.flatMap((batch) => batch.items),
    [batches]
  );

  const selectedTask = tasks.find((task) => task.id === selectedTaskId) ?? null;
  const taskResults = useMemo(
    () => results.filter((result) => result.task_id === selectedTaskId),
    [results, selectedTaskId]
  );

  // 从改派/排队结果反查当前任务的联动
  const taskEvents = useMemo<TimelineEntry[]>(() => {
    if (!selectedTask) return [];
    const entries: TimelineEntry[] = [];
    outageItems.forEach((item) => {
      item.reroute?.rerouted
        .filter((r) => r.task_id === selectedTask.id)
        .forEach((r, index) => {
          const backup = devices.find((device) => device.id === r.backup_device_id);
          const original = devices.find((device) => device.id === item.device_id);
          entries.push({
            id: `${item.id}-r-${index}`,
            title: `停用 #${item.id}：原检 ${original?.device_code ?? "#" + item.device_id} → 备用 ${backup?.device_code ?? "#" + r.backup_device_id}`,
            time: `${formatShortDate(item.start_at)} 起`,
            tone: "#274335"
          });
        });
      item.reroute?.queued
        .filter((q) => q.task_id === selectedTask.id)
        .forEach((q, index) => {
          entries.push({
            id: `${item.id}-q-${index}`,
            title: `停用 #${item.id}：备用容量不足，排队待补检`,
            time: `${formatShortDate(item.start_at)} 起`,
            tone: "#8a5a12"
          });
        });
    });
    return entries;
  }, [selectedTask, outageItems, devices]);

  const review = async (resultId: number, action: "REINSTATE" | "CONFIRM_VOID") => {
    try {
      await reviewVoidedResult(resultId, action);
      notify(action === "REINSTATE" ? "结果已恢复有效" : "已确认作废", "success");
      void dispatch(fetchInspectionResults());
    } catch (error) {
      notifyError(error);
    }
  };

  return (
    <Box sx={{ display: "grid", gap: 3 }}>
      <PageHeader title="巡检任务" />

      <FilterBar
        filters={[{ label: "任务状态", value: statusFilter, options: InspectionStatusOptions, onChange: setStatusFilter }]}
      />

      <Paper variant="outlined" sx={{ borderRadius: 3, overflow: "hidden" }}>
        {tasks.length === 0 ? (
          <Box sx={{ p: 3 }}><EmptyState title="暂无巡检任务" /></Box>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>任务</TableCell>
                <TableCell>计划时间</TableCell>
                <TableCell>类型</TableCell>
                <TableCell>状态</TableCell>
                <TableCell>检查项</TableCell>
                <TableCell align="right">详情</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.map((task) => {
                const taskRows = results.filter((result) => result.task_id === task.id);
                const voided = taskRows.filter((result) => result.review_flag === "VOID_PENDING_REVIEW");
                return (
                  <TableRow key={task.id} hover>
                    <TableCell sx={{ fontWeight: 700 }}>#{task.id} · 楼栋 #{task.building_id}</TableCell>
                    <TableCell>{formatShortDate(task.plan_date)}</TableCell>
                    <TableCell>{formatStatus("DeviceType", task.task_type)}</TableCell>
                    <TableCell><StatusBadge value={task.status} kind="InspectionStatus" /></TableCell>
                    <TableCell>
                      <Stack direction="row" spacing={0.5}>
                        <Chip size="small" label={`${taskRows.length} 项`} />
                        {voided.length > 0 ? <Chip size="small" color="error" label={`${voided.length} 待复核`} /> : null}
                      </Stack>
                    </TableCell>
                    <TableCell align="right">
                      <Button size="small" onClick={() => setSelectedTaskId(task.id)}>查看改派/检查项</Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </Paper>

      <Dialog open={selectedTask !== null} onClose={() => setSelectedTaskId(null)} fullWidth maxWidth="md">
        <DialogTitle>
          巡检任务 #{selectedTask?.id}
          {selectedTask ? <StatusBadge value={selectedTask.status} kind="InspectionStatus" /> : null}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid xs={12} md={6}>
              <ChecklistPanel results={taskResults} />
              <Box sx={{ mt: 2 }}>
                <TimelineList title="停用联动（原任务关系保留）" entries={taskEvents} />
              </Box>
            </Grid>
            <Grid xs={12} md={6}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>检查项明细</Typography>
              {taskResults.length === 0 ? (
                <EmptyState title="暂无检查项" />
              ) : (
                <Stack spacing={1}>
                  {taskResults.map((result) => {
                    const device = devices.find((row) => row.id === result.device_id);
                    return (
                      <Paper key={result.id} variant="outlined" sx={{ p: 1.5 }}>
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 700 }}>
                              {result.item_code} · {device?.device_code ?? `设备#${result.device_id}`}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {result.result_status === "ABNORMAL" ? "异常" : "正常"} · {result.measured_value ?? "—"}
                            </Typography>
                          </Box>
                          {result.review_flag === "VOID_PENDING_REVIEW" ? (
                            <Stack direction="row" spacing={1}>
                              <Chip size="small" color="error" label="作废待复核" />
                              {canReview ? (
                                <>
                                  <Button size="small" onClick={() => void review(result.id, "REINSTATE")}>恢复</Button>
                                  <Button size="small" color="inherit" onClick={() => void review(result.id, "CONFIRM_VOID")}>
                                    确认作废
                                  </Button>
                                </>
                              ) : (
                                <Typography variant="caption" color="text.secondary">待主管/审计复核</Typography>
                              )}
                            </Stack>
                          ) : (
                            <Chip size="small" label={result.review_flag === "ACTIVE" ? "有效" : "已作废"} />
                          )}
                        </Stack>
                      </Paper>
                    );
                  })}
                </Stack>
              )}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedTaskId(null)}>关闭</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
