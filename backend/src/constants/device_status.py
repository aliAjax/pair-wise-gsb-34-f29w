# 设备生命周期状态：正常 / 停用 / 待复役（手续未齐）/ 待修
# PENDING_REUSE 表示停用结束但复役手续未补齐，不能回到 NORMAL
DeviceStatus = ["NORMAL", "OUTAGE", "PENDING_REUSE", "FAULT"]

DEVICE_STATUS_LABELS = {
    "NORMAL": "正常",
    "OUTAGE": "停用中",
    "PENDING_REUSE": "待复役",
    "FAULT": "待修",
}
