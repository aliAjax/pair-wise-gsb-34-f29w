# 停用时段状态
# DRAFT：与他人已确认时段重叠，后到者只能保留草稿，并看到占用数量
# CONFIRMED：已确认生效；SUPERSEDED：时段被修改，旧版本作废
# CANCELLED：停用撤销；PENDING：写入失败后待续跑
OutageStatus = ["DRAFT", "CONFIRMED", "SUPERSEDED", "CANCELLED", "PENDING"]

OUTAGE_STATUS_LABELS = {
    "DRAFT": "草稿",
    "CONFIRMED": "已确认",
    "SUPERSEDED": "已作废",
    "CANCELLED": "已撤销",
    "PENDING": "待续传",
}

# 同栋同类型备用设备在重叠窗口内可承担的巡检槽位（容量）；
# 超出容量的受影响任务排队转成 PENDING_MAKEUP 待补检
BACKUP_SLOT_CAPACITY = 1
