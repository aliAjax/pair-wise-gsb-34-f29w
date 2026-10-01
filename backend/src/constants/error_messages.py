"""错误消息模板，与 error_codes 分离，字段变更需同步两处。"""

ERROR_MESSAGES = {
    "AUTH_REQUIRED": "缺少认证令牌，请先登录",
    "RBAC_DENIED": "当前角色无权执行该操作：需要 {required}",
    "VALIDATION_FAILED": "请求参数校验失败：{detail}",
    "NOT_FOUND": "{resource} 不存在：{entity_id}",
    "CONFLICT": "资源冲突：{detail}",
    "INTERNAL_ERROR": "服务内部错误，请稍后重试",
    "OUTAGE_WINDOW_NOT_FOUND": "停用时段不存在：{window_id}",
    "OUTAGE_WINDOW_INVALID_RANGE": "停用时段非法：开始时间必须早于结束时间（{start_at} ~ {end_at}）",
    "OUTAGE_ALREADY_CONFIRMED": "停用时段已确认，无法重复确认：{window_id}",
    "OUTAGE_DRAFT_VERSION_STALE": "草稿版本已过期，请刷新占用数量后重试（当前版本 {version}）",
    "OUTAGE_RESUME_KEY_MISMATCH": "恢复键与最近一次失败写入不匹配",
    "OUTAGE_WRITE_STAGE_UNKNOWN": "未知的写入阶段：{stage}",
    "BACKUP_CAPACITY_EXHAUSTED": "备用设备容量不足：同栋同类型可用 {available}，已占用 {occupied}，需求 {demanded}",
    "ASSIGNMENT_NOT_FOUND": "巡检排期记录不存在：{assignment_id}",
    "DEVICE_NOT_OUT_OF_SERVICE": "设备当前并非停用状态，无法复役：{device_code}",
    "RESTORE_PROCEDURE_INCOMPLETE": "设备 {device_code} 复役前手续未补齐，缺少：{missing}",
    "REVIEW_RECORD_NOT_FOUND": "待复核记录不存在：{record_type}#{record_id}",
}
