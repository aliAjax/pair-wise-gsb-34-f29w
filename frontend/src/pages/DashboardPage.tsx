import { useEffect } from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";

import { listAuditLogs } from "../api/Dashboard";
import { DeviceStatusText } from "../constants/DeviceStatus";
import { InspectionStatusText } from "../constants/InspectionStatus";
import { PageHeader } from "../components/common/PageHeader";
import { StatCard } from "../components/common/StatCard";
import { StatusBadge } from "../components/common/StatusBadge";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { EmptyState } from "../components/common/EmptyState";
import { fetchBuildings } from "../stores/BuildingStore";
import { fetchHazardTickets } from "../stores/HazardTicketStore";
import { fetchDashboardSummary } from "../stores/DashboardStore";
import { useAppDispatch, useAppSelector } from "../stores/hooks";
import { formatDate, formatPercent } from "../utils/formatters";
import { useState } from "react";
import type { AuditLog } from "../types/Dashboard";

export function DashboardPage() {
  const dispatch = useAppDispatch();
  const summary = useAppSelector((state) => state.dashboard.data);
  const devices = useAppSelector((state) => state.fireDevice.rows);
  const tasks = useAppSelector((state) => state.inspectionTask.rows);
  const tickets = useAppSelector((state) => state.hazardTicket.rows);
  const [logs, setLogs] = useState<AuditLog[]>([]);

  useEffect(() => {
    void dispatch(fetchDashboardSummary());
    void dispatch(fetchBuildings());
    void dispatch(fetchHazardTickets());
    listAuditLogs(12).then(setLogs).catch(() => setLogs([]));
  }, [dispatch]);

  const critical = tickets.filter(
    (ticket) => ticket.severity === "CRITICAL" && ticket.rectify_status !== "VERIFIED"
  );
  const voidPending = tickets.filter((ticket) => ticket.rectify_status === "VOID_PENDING_REVIEW");
  const makeup = tasks.filter((task) => task.status === "PENDING_MAKEUP");

  return (
    <Box sx={{ display: "grid", gap: 3 }}>
      <PageHeader title="消防合规总览" actions={<StatusBadge value={summary ? "ACTIVE" : "PENDING"} />} />

      <Grid container spacing={2}>
        <Grid xs={12} sm={6} md={3}>
          <StatCard label="在册设备" value={summary?.device_total ?? "—"} hint="含停用/待复役" />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard
            label="巡检完成率"
            value={summary ? formatPercent(summary.inspection_completion_rate) : "—"}
            hint={`待补检排队 ${summary?.pending_makeup_task_ids.length ?? 0} 单`}
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard
            label="未闭环隐患"
            value={summary?.open_ticket_count ?? "—"}
            hint={`严重 ${summary?.critical_ticket_count ?? 0} 单`}
          />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard
            label="停用变化待复核"
            value={summary?.void_pending_ticket_count ?? 0}
            hint={`已确认停用 ${summary?.outage_confirmed_count ?? 0} · 冲突草稿 ${summary?.outage_draft_count ?? 0}`}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 2, borderRadius: 3 }} variant="outlined">
            <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>
              设备状态分布
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>状态</TableCell>
                  <TableCell align="right">数量</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(summary?.device_status_distribution ?? {}).map(([status, count]) => (
                  <TableRow key={status}>
                    <TableCell><StatusBadge value={status} kind="DeviceStatus" /></TableCell>
                    <TableCell align="right">{count} · {DeviceStatusText[status as keyof typeof DeviceStatusText] ?? status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 2, borderRadius: 3 }} variant="outlined">
            <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>
              巡检任务状态分布
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>状态</TableCell>
                  <TableCell align="right">数量</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(summary?.task_status_distribution ?? {}).map(([status, count]) => (
                  <TableRow key={status}>
                    <TableCell><StatusBadge value={status} kind="InspectionStatus" /></TableCell>
                    <TableCell align="right">{count} · {InspectionStatusText[status as keyof typeof InspectionStatusText] ?? status}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 2, borderRadius: 3 }} variant="outlined">
            <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>
              高危隐患 / 作废待复核
            </Typography>
            {critical.length === 0 && voidPending.length === 0 ? (
              <EmptyState title="暂无高危或待复核隐患" />
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>单号</TableCell>
                    <TableCell>级别</TableCell>
                    <TableCell>设备</TableCell>
                    <TableCell>状态</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {[...critical, ...voidPending].map((ticket) => (
                    <TableRow key={ticket.id}>
                      <TableCell>#{ticket.id}</TableCell>
                      <TableCell><HazardSeverityTag value={ticket.severity} /></TableCell>
                      <TableCell>#{ticket.device_id}</TableCell>
                      <TableCell>
                        <StatusBadge
                          value={ticket.rectify_status}
                          kind={ticket.rectify_status.includes("VOID") ? "OutageStatus" : undefined}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
            {makeup.length > 0 ? (
              <Typography variant="caption" color="#8a5a12" sx={{ mt: 1, display: "block" }}>
                备用容量不足排队待补检任务：{makeup.map((task) => `#${task.id}`).join("、")}
              </Typography>
            ) : null}
          </Paper>
        </Grid>
        <Grid xs={12} md={6}>
          <Paper sx={{ p: 2, borderRadius: 3 }} variant="outlined">
            <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>
              最近操作日志
            </Typography>
            {logs.length === 0 ? (
              <EmptyState title="暂无日志" />
            ) : (
              <Box sx={{ display: "grid", gap: 1 }}>
                {logs.map((log) => (
                  <Box key={log.id} sx={{ borderLeft: "3px solid #d39b46", pl: 1.5, py: 0.5 }}>
                    <Typography variant="body2">{log.detail}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {log.actor} · {formatDate(log.created_at)}
                    </Typography>
                  </Box>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
      {devices.length === 0 ? null : null}
    </Box>
  );
}
