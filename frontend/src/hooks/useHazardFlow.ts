import { useMemo, useState } from "react";
import type { HazardTicket } from "../types/HazardTicket";

// 隐患整改流程：待派单/待整改/待复验/作废待复核 分栏统计
export function useHazardFlow(rows: HazardTicket[] = []) {
  const [filter, setFilter] = useState<string>("ALL");
  const buckets = useMemo(
    () => ({
      open: rows.filter((r) => r.rectify_status === "OPEN"),
      assigned: rows.filter((r) => r.rectify_status === "ASSIGNED"),
      rectified: rows.filter((r) => r.rectify_status === "RECTIFIED"),
      voidPending: rows.filter((r) => r.rectify_status === "VOID_PENDING_REVIEW"),
      verified: rows.filter((r) => r.rectify_status === "VERIFIED")
    }),
    [rows]
  );
  const visible = useMemo(
    () => (filter === "ALL" ? rows : rows.filter((r) => r.rectify_status === filter)),
    [rows, filter]
  );
  return { filter, setFilter, buckets, visible };
}
