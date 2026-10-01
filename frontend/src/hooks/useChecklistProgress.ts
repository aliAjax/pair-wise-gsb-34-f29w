import { useMemo } from "react";

export interface ChecklistItem {
  item_code: string;
  result_status?: string;
}

/**
 * 巡检清单完成进度：按检查项数量计算完成数 / 总数 / 百分比。
 * 任务页 ChecklistPanel 与提交按钮显隐共同依赖。
 */
export function useChecklistProgress(items: ChecklistItem[] = []) {
  return useMemo(() => {
    const total = items.length;
    const completed = items.filter(
      (i) => i.result_status && i.result_status !== "PENDING"
    ).length;
    const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
    return { total, completed, percent, isComplete: total > 0 && completed === total };
  }, [items]);
}
