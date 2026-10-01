import { useEffect } from "react";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";

import { reviewOrCloseHazardTicket } from "../api/HazardTicket";
import { DEMO_USERS } from "../constants/roles";
import { HazardSeverityTag } from "../components/common/HazardSeverityTag";
import { PageHeader } from "../components/common/PageHeader";
import { StatusBadge } from "../components/common/StatusBadge";
import { TimelineList, type TimelineEntry } from "../components/common/TimelineList";
import { EmptyState } from "../components/common/EmptyState";
import { useToast } from "../components/common/Toast";
import { fetchFireDevices } from "../stores/FireDeviceStore";
import { fetchHazardTickets } from "../stores/HazardTicketStore";
import { useHazardFlow } from "../hooks/useHazardFlow";
import { useAppDispatch, useAppSelector } from "../stores/hooks";
import { formatDate } from "../utils/formatters";

const FILTERS = [
  { value: "ALL", label: "全部" },
  { value: "OPEN", label: "待派单" },
  { value: "ASSIGNED", label: "待整改" },
  { value: "RECTIFIED", label: "待复验" },
  { value: "VOID_PENDING_REVIEW", label: "作废待复核" },
  { value: "VERIFIED", label: "已关闭" }
];

export function HazardsPage() {
  const dispatch = useAppDispatch();
  const { notify, notifyError } = useToast();
  const tickets = useAppSelector((state) => state.hazardTicket.rows);
  const devices = useAppSelector((state) => state.fireDevice.rows);
  const { filter, setFilter, buckets, visible } = useHazardFlow(tickets);
  const actorId = useAppSelector((state) => state.session.actorId);
  const actor = DEMO_USERS.find((user) => user.id === actorId) ?? DEMO_USERS[2];
  // 复验关闭与作废复核仅主管/审计；维保商可整改回填（本页只读展示流程）
  const canReview = actor.role === "SUPERVISOR" || actor.role === "AUDITOR";

  useEffect(() => {
    void dispatch(fetchFireDevices());
    void dispatch(fetchHazardTickets());
  }, [dispatch]);

  const act = async (ticketId: number, action: "REINSTATE" | "CONFIRM_VOID" | "CLOSE") => {
    try {
      await reviewOrCloseHazardTicket(ticketId, action);
      notify(
        action === "REINSTATE" ? "隐患单已恢复有效" : action === "CONFIRM_VOID" ? "已确认作废" : "复验关闭成功",
        "success"
      );
      void dispatch(fetchHazardTickets());
    } catch (error) {
      notifyError(error);
    }
  };

  const buildTimeline = (ticket: (typeof tickets)[number]): TimelineEntry[] => {
    const entries: TimelineEntry[] = [
      { id: "create", title: `异常结果 #${ticket.result_id} 触发隐患单`, tone: "#8a2b2b" }
    ];
    if (ticket.owner_id) entries.push({ id: "dispatch", title: `派单给责任人 #${ticket.owner_id}`, tone: "#27435f" });
    if (ticket.rectify_note) entries.push({ id: "rectify", title: `整改回填：${ticket.rectify_note}`, tone: "#7d4d18" });
    if (ticket.rectify_status === "VOID_PENDING_REVIEW") {
      entries.push({
        id: "void",
        title: `停用时段 #${ticket.voided_by_outage_id} 变化，隐患单作废待复核`,
        time: formatDate(ticket.voided_at),
        tone: "#8a2b2b"
      });
    }
    if (ticket.rectify_status === "VERIFIED") {
      entries.push({ id: "close", title: "复验关闭", time: formatDate(ticket.closed_at), tone: "#244b31" });
    }
    return entries;
  };

  return (
    <Box sx={{ display: "grid", gap: 3 }}>
      <PageHeader title="隐患整改" />

      <Stack direction="row" spacing={1} flexWrap="wrap">
        {FILTERS.map((item) => {
          const count =
            item.value === "ALL"
              ? tickets.length
              : item.value === "OPEN"
                ? buckets.open.length
                : item.value === "ASSIGNED"
                  ? buckets.assigned.length
                  : item.value === "RECTIFIED"
                    ? buckets.rectified.length
                    : item.value === "VOID_PENDING_REVIEW"
                      ? buckets.voidPending.length
                      : buckets.verified.length;
          return (
            <Button
              key={item.value}
              size="small"
              variant={filter === item.value ? "contained" : "outlined"}
              onClick={() => setFilter(item.value)}
              sx={{ bgcolor: filter === item.value ? "#274335" : undefined }}
            >
              {item.label}（{count}）
            </Button>
          );
        })}
      </Stack>

      {visible.length === 0 ? (
        <EmptyState title="当前筛选下没有隐患单" />
      ) : (
        visible.map((ticket) => {
          const device = devices.find((row) => row.id === ticket.device_id);
          return (
            <Paper key={ticket.id} variant="outlined" sx={{ p: 2, borderRadius: 3 }}>
              <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                <Box sx={{ flex: 2 }}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    <Typography sx={{ fontWeight: 800 }}>隐患单 #{ticket.id}</Typography>
                    <HazardSeverityTag value={ticket.severity} />
                    <StatusBadge
                      value={ticket.rectify_status}
                      kind={ticket.rectify_status.includes("VOID") ? "OutageStatus" : undefined}
                    />
                  </Stack>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>设备</TableCell>
                        <TableCell>责任人</TableCell>
                        <TableCell>整改期限</TableCell>
                        <TableCell>整改说明</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>{device?.device_code ?? `设备#${ticket.device_id}`}</TableCell>
                        <TableCell>{ticket.owner_id ? `#${ticket.owner_id}` : "未派单"}</TableCell>
                        <TableCell>{formatDate(ticket.deadline)}</TableCell>
                        <TableCell>{ticket.rectify_note ?? "—"}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </Box>
                <Box sx={{ flex: 1 }}>
                  <TimelineList title="处理时间线" entries={buildTimeline(ticket)} />
                  <Stack direction="row" spacing={1} sx={{ mt: 1.5 }}>
                    {ticket.rectify_status === "VOID_PENDING_REVIEW" ? (
                      canReview ? (
                        <>
                          <Button size="small" variant="contained" onClick={() => void act(ticket.id, "REINSTATE")}>
                            恢复有效
                          </Button>
                          <Button size="small" color="inherit" onClick={() => void act(ticket.id, "CONFIRM_VOID")}>
                            确认作废
                          </Button>
                        </>
                      ) : (
                        <Typography variant="caption" color="text.secondary">待主管/审计复核</Typography>
                      )
                    ) : ticket.rectify_status === "RECTIFIED" ? (
                      canReview ? (
                        <Button size="small" variant="contained" onClick={() => void act(ticket.id, "CLOSE")}>
                          复验关闭
                        </Button>
                      ) : (
                        <Typography variant="caption" color="text.secondary">待主管复验</Typography>
                      )
                    ) : ticket.rectify_status === "VERIFIED" ? (
                      <Typography variant="caption" sx={{ color: "#244b31", fontWeight: 700 }}>
                        已于 {formatDate(ticket.closed_at)} 关闭
                      </Typography>
                    ) : (
                      <Typography variant="caption" color="text.secondary">
                        等待整改回填后复验
                      </Typography>
                    )}
                  </Stack>
                </Box>
              </Stack>
            </Paper>
          );
        })
      )}
    </Box>
  );
}
