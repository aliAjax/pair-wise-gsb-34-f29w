# 巡检任务状态枚举（前端 constants/InspectionStatus.ts 必须保持同步）
# PENDING_MAKEUP：备用设备容量不足时排队转成的“待补检”
InspectionStatus = [
    "PLANNED",
    "IN_PROGRESS",
    "SUBMITTED",
    "REVIEWED",
    "OVERDUE",
    "PENDING_MAKEUP",
]

INSPECTION_STATUS_LABELS = {
    "PLANNED": "已排期",
    "IN_PROGRESS": "进行中",
    "SUBMITTED": "待复核",
    "REVIEWED": "已复核",
    "OVERDUE": "已逾期",
    "PENDING_MAKEUP": "待补检",
}
