# 错误消息模板集中定义；新增字段/状态时这里必须同步。
# {placeholder} 由 service 层 str.format 填充。
ERROR_MESSAGES = {
    "AUTH_REQUIRED": "缺少有效的身份凭证，请重新登录",
    "RBAC_DENIED": "当前角色 {role} 无权执行 {action}",
    "VALIDATION_FAILED": "参数校验失败：{detail}",
    "RATE_LIMITED": "请求过于频繁，请稍后再试",
    "DEVICE_NOT_FOUND": "消防设备 {device_id} 不存在",
    "DEVICE_NOT_OUTAGE": "设备 {device_id} 当前不处于停用中，不能复役",
    "PAPERWORK_INCOMPLETE": "设备 {device_id} 复役手续未补齐（缺 {missing}），不能回到正常",
    "OUTAGE_NOT_FOUND": "停用时段 {outage_id} 不存在",
    "OUTAGE_WINDOW_INVALID": "停用时段非法：开始时间必须早于结束时间",
    "OUTAGE_OVERLAP_DRAFT": "与 {occupied_count} 个已确认停用名额冲突，已保留为草稿",
    "OUTAGE_BATCH_NOT_FOUND": "停用批次 {batch_id} 不存在",
    "OUTAGE_BATCH_NOT_RESUMABLE": "停用批次 {batch_id} 没有可续传的失败项",
    "TASK_NOT_FOUND": "巡检任务 {task_id} 不存在",
    "RESULT_NOT_FOUND": "巡检结果 {result_id} 不存在",
    "TICKET_NOT_FOUND": "隐患整改单 {ticket_id} 不存在",
    "BUILDING_NOT_FOUND": "楼栋 {building_id} 不存在",
    "WRITE_FAILED": "写入失败：{detail}",
    "CONFLICT_STATE": "数据状态已被他人更新，请刷新后重试",
}

# 复役手续清单；设备复役接口逐项核对
REUSE_PAPERWORK_ITEMS = ["MAINTENANCE_REPORT", "SAFETY_CHECK", "MANAGER_SIGN_OFF"]

REUSE_PAPERWORK_LABELS = {
    "MAINTENANCE_REPORT": "维保报告",
    "SAFETY_CHECK": "安全检测",
    "MANAGER_SIGN_OFF": "主管签字",
}
