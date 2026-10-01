import { useMemo } from "react";
import type { InspectionResult } from "../types/InspectionResult";

// 巡检检查项完成度：任务页 ChecklistPanel 用
export function useChecklistProgress(results: InspectionResult[] = []) {
  const total = results.length;
  const done = results.filter((row) => row.review_flag === "ACTIVE").length;
  const voided = results.filter((row) => row.review_flag === "VOID_PENDING_REVIEW").length;
  return useMemo(
    () => ({
      total,
      done,
      voided,
      percent: total === 0 ? 0 : Math.round((done / total) * 100)
    }),
    [total, done, voided]
  );
}
