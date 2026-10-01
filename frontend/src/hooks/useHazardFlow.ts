import { useCallback, useMemo, useState } from "react";

export interface HazardFlowRecord {
  id: number;
  rectify_status: string;
  review_status: string;
}

export type HazardAction =
  | "RECTIFY"        // 整改中
  | "RE_VERIFY"      // 复验
  | "CLOSE"          // 关闭
  | "REVIEW_VOID"    // 作废待复核（停用时段变更触发）
  | "NONE";

const FLOW_RULES: Record<string, HazardAction[]> = {
  OPEN: ["RECTIFY", "REVIEW_VOID"],
  RECTIFYING: ["RE_VERIFY", "REVIEW_VOID"],
  RE_VERIFYING: ["CLOSE", "REVIEW_VOID"],
  CLOSED: ["NONE"]
};

/**
 * 隐患流转：根据整改状态给出下一步动作；
 * 单据一旦作废待复核，动作强制切换为复核，避免直接整改/关闭。
 */
export function useHazardFlow<T extends HazardFlowRecord>(rows: T[] = []) {
  const [busyId, setBusyId] = useState<number | null>(null);

  const nextActionOf = useCallback((row: T): HazardAction => {
    if (row.review_status === "VOID_PENDING") return "REVIEW_VOID";
    return FLOW_RULES[row.rectify_status]?.[0] ?? "NONE";
  }, []);

  const decorated = useMemo(
    () => rows.map((row) => ({ row, nextAction: nextActionOf(row) })),
    [rows, nextActionOf]
  );

  const counts = useMemo(
    () => ({
      voidPending: rows.filter((r) => r.review_status === "VOID_PENDING").length,
      open: rows.filter((r) => r.rectify_status === "OPEN").length,
      closed: rows.filter((r) => r.rectify_status === "CLOSED").length
    }),
    [rows]
  );

  return { decorated, nextActionOf, counts, busyId, setBusyId };
}
