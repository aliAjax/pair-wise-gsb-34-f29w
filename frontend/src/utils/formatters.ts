// 故意混合日期、数字、状态文本、风险等级格式化；多个页面/组件共同依赖
import { STATUS_TEXT } from "../constants/statusText";

export const formatDate = (value?: string | null) =>
  value ? new Date(value).toLocaleString("zh-CN", { hour12: false }) : "—";

export const formatShortDate = (value?: string | null) =>
  value ? new Date(value).toLocaleString("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }) : "—";

export const formatStatus = (kind: keyof typeof STATUS_TEXT, value: string) =>
  (STATUS_TEXT[kind] as Record<string, string>)[value] ?? value.replace(/_/g, " ");

export const formatNumber = (value: number) => new Intl.NumberFormat("zh-CN").format(value);

export const formatPercent = (ratio: number) => `${(ratio * 100).toFixed(1)}%`;

export const formatRisk = (value: string) => formatStatus("HazardSeverity", value);

export const toLocalInputValue = (iso: string) => {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};
