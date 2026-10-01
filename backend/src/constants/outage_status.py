"""停用时段状态。"""

OutageStatus = [
    "DRAFT",       # 草稿：后到负责人看到占用数量后保留的草稿
    "CONFIRMED",   # 已确认：设备真正进入停用
    "SUPERSEDED",  # 被变更替代（时段调整后旧版本作废）
]

OutageStatusText = {
    "DRAFT": "草稿",
    "CONFIRMED": "已确认",
    "SUPERSEDED": "已变更",
}
