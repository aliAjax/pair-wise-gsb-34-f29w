"""设备生命周期状态。与前端 constants/DeviceStatus.ts 重复定义，新增值需多处同步。"""

DeviceStatus = [
    "NORMAL",          # 正常在用
    "OUT_OF_SERVICE",  # 停用保养中
    "RESTORED",        # 已复役
]

DeviceStatusText = {
    "NORMAL": "正常",
    "OUT_OF_SERVICE": "停用",
    "RESTORED": "已复役",
}
