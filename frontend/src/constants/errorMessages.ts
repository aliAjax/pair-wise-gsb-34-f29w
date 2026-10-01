export const ERROR_MESSAGES = {
  AUTH_REQUIRED: "请先登录后再继续操作",
  RBAC_DENIED: "当前角色没有执行该动作的权限",
  VALIDATION_FAILED: "表单字段缺失或格式错误",
  RATE_LIMITED: "请求过于频繁，请稍后再试",
  NOT_FOUND: "记录不存在",
  CONFLICT: "资源冲突或写入失败",
  INTERNAL_ERROR: "服务内部错误，请稍后重试",
  OUTAGE_WINDOW_NOT_FOUND: "停用时段不存在",
  OUTAGE_WINDOW_INVALID_RANGE: "停用时段开始时间必须早于结束时间",
  OUTAGE_ALREADY_CONFIRMED: "停用时段已确认，请勿重复提交",
  OUTAGE_DRAFT_VERSION_STALE: "草稿版本已过期，请刷新占用数量后重试",
  OUTAGE_RESUME_KEY_MISMATCH: "恢复键不匹配，无法断点续跑",
  OUTAGE_WRITE_STAGE_UNKNOWN: "未知的写入阶段",
  BACKUP_CAPACITY_EXHAUSTED: "备用设备容量不足，已转入待补检队列",
  DEVICE_NOT_OUT_OF_SERVICE: "设备当前并非停用状态",
  RESTORE_PROCEDURE_INCOMPLETE: "复役前手续未补齐，设备不能回到正常",
  REVIEW_RECORD_NOT_FOUND: "待复核记录不存在"
} as const;
