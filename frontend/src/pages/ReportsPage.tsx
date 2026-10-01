import { useEffect, useMemo } from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

import { DeviceStatusText } from "../constants/DeviceStatus";
import { InspectionStatusText } from "../constants/InspectionStatus";
import { HazardSeverityText } from "../constants/HazardSeverity";
import { PageHeader } from "../components/common/PageHeader";
import { StatCard } from "../components/common/StatCard";
import { EmptyState } from "../components/common/EmptyState";
import { fetchDashboardSummary } from "../stores/DashboardStore";
import { fetchFireDevices } from "../stores/FireDeviceStore";
import { fetchHazardTickets } from "../stores/HazardTicketStore";
import { fetchInspectionTasks } from "../stores/InspectionTaskStore";
import { useAppDispatch, useAppSelector } from "../stores/hooks";
import { formatPercent } from "../utils/formatters";

function BarRow({ label, value, max, color = "#274335" }: { label: string; value: number; max: number; color?: string }) {
  const width = max === 0 ? 0 : Math.round((value / max) * 100);
  return (
    <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.8 }}>
      <Typography variant="caption" sx={{ width: 96, flexShrink: 0 }}>{label}</Typography>
      <Box sx={{ flex: 1, bgcolor: "#ece7dd", borderRadius: 99, height: 14 }}>
        <Box sx={{ width: `${width}%`, bgcolor: color, height: "100%", borderRadius: 99, transition: "width .3s" }} />
      </Box>
      <Typography variant="caption" sx={{ width: 28, textAlign: "right", fontWeight: 700 }}>{value}</Typography>
    </Stack>
  );
}

export function ReportsPage() {
  const dispatch = useAppDispatch();
  const summary = useAppSelector((state) => state.dashboard.data);
  const devices = useAppSelector((state) => state.fireDevice.rows);
  const tasks = useAppSelector((state) => state.inspectionTask.rows);
  const tickets = useAppSelector((state) => state.hazardTicket.rows);

  useEffect(() => {
    void dispatch(fetchDashboardSummary());
    void dispatch(fetchFireDevices());
    void dispatch(fetchInspectionTasks());
    void dispatch(fetchHazardTickets());
  }, [dispatch]);

  const severityStats = useMemo(() => {
    const map: Record<string, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
    tickets.forEach((ticket) => {
      if (ticket.rectify_status !== "VERIFIED") map[ticket.severity] = (map[ticket.severity] ?? 0) + 1;
    });
    return map;
  }, [tickets]);

  const rectifyRate = tickets.length === 0
    ? 0
    : tickets.filter((ticket) => ticket.rectify_status === "VERIFIED").length / tickets.length;

  const outageRate = tasks.length === 0
    ? 0
    : tasks.filter((task) => task.status === "PENDING_MAKEUP").length / tasks.length;

  return (
    <Box sx={{ display: "grid", gap: 3 }}>
      <PageHeader title="合规报表" eyebrow="月度合规台账" />

      <Grid container spacing={2}>
        <Grid xs={12} sm={6} md={3}>
          <StatCard label="巡检完成率" value={formatPercent(summary?.inspection_completion_rate ?? 0)} />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard label="整改关闭率" value={formatPercent(rectifyRate)} hint={`共 ${tickets.length} 张隐患单`} />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard label="停用待补检率" value={formatPercent(outageRate)} hint="备用容量不足导致" />
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <StatCard
            label="作废待复核"
            value={summary?.void_pending_ticket_count ?? 0}
            hint={`结果/隐患单引用了停用设备`}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>设备故障率（按状态）</Typography>
            {devices.length === 0 ? <EmptyState title="暂无设备" /> : (
              (() => {
                const map: Record<string, number> = {};
                devices.forEach((d) => { map[d.status] = (map[d.status] ?? 0) + 1; });
                const max = Math.max(1, ...Object.values(map));
                return Object.keys(DeviceStatusText).map((key) => (
                  <BarRow
                    key={key}
                    label={DeviceStatusText[key as keyof typeof DeviceStatusText]}
                    value={map[key] ?? 0}
                    max={max}
                    color={key === "NORMAL" ? "#274335" : key === "OUTAGE" ? "#8a2b2b" : "#8a5a12"}
                  />
                ));
              })()
            )}
          </Paper>
        </Grid>
        <Grid xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>巡检任务状态</Typography>
            {tasks.length === 0 ? <EmptyState title="暂无任务" /> : (
              (() => {
                const map: Record<string, number> = {};
                tasks.forEach((t) => { map[t.status] = (map[t.status] ?? 0) + 1; });
                const max = Math.max(1, ...Object.values(map));
                return Object.keys(InspectionStatusText).map((key) => (
                  <BarRow
                    key={key}
                    label={InspectionStatusText[key as keyof typeof InspectionStatusText]}
                    value={map[key] ?? 0}
                    max={max}
                    color={key === "PENDING_MAKEUP" ? "#8a5a12" : "#27435f"}
                  />
                ));
              })()
            )}
          </Paper>
        </Grid>
        <Grid xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 2, borderRadius: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>未关闭隐患分级</Typography>
            {tickets.length === 0 ? <EmptyState title="暂无隐患" /> : (
              (() => {
                const max = Math.max(1, ...Object.values(severityStats));
                return Object.keys(HazardSeverityText).map((key) => (
                  <BarRow
                    key={key}
                    label={HazardSeverityText[key as keyof typeof HazardSeverityText]}
                    value={severityStats[key] ?? 0}
                    max={max}
                    color={key === "CRITICAL" ? "#8a2b2b" : key === "HIGH" ? "#9a5410" : "#274335"}
                  />
                ));
              })()
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
