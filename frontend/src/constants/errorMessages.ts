import type { ErrorCode } from "./errorCodes";

export const ERROR_MESSAGES: Record<ErrorCode, string> = {
  AUTH_REQUIRED: "请先登录后再继续操作",
  RBAC_DENIED: "当前角色没有执行该动作的权限",
  VALIDATION_FAILED: "表单字段缺失或格式错误",
  RATE_LIMITED: "请求过于频繁，请稍后再试",
  DEVICE_NOT_FOUND: "消防设备不存在",
  DEVICE_NOT_OUTAGE: "设备当前不处于停用中，不能复役",
  PAPERWORK_INCOMPLETE: "复役手续未补齐，设备暂挂待复役，不能回到正常",
  OUTAGE_NOT_FOUND: "停用时段不存在",
  OUTAGE_WINDOW_INVALID: "停用时段非法：开始时间必须早于结束时间",
  OUTAGE_OVERLAP_DRAFT: "与已确认停用名额冲突，已保留为草稿",
  OUTAGE_BATCH_NOT_FOUND: "停用批次不存在",
  OUTAGE_BATCH_NOT_RESUMABLE: "该批次没有可续传的失败项",
  WRITE_FAILED: "写入失败，请稍后重试或使用续传",
  CONFLICT_STATE: "数据状态已被他人更新，请刷新后重试"
};
