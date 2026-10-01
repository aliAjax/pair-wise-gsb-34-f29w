"""停用变更触发的复核状态：引用停用设备的巡检结果与隐患整改单一律作废待复核。"""

ReviewStatus = [
    "ACTIVE",            # 有效
    "VOID_PENDING",      # 作废待复核
    "RECONFIRMED",       # 复核后重新确认有效
    "REJECTED",          # 复核后维持作废
]

ReviewStatusText = {
    "ACTIVE": "有效",
    "VOID_PENDING": "作废待复核",
    "RECONFIRMED": "复核通过",
    "REJECTED": "维持作废",
}
