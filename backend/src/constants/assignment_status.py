"""巡检排期（任务-设备关系）状态。

原任务关系始终保留：ORIGINAL 行不会被删除，只是在停用期间被 BACKUP 行替代
或转为 PENDING_RECHECK（待补检）。
"""

AssignmentStatus = [
    "ORIGINAL",         # 原计划：任务原本绑定的设备
    "BACKUP",           # 停用期间改用备用设备
    "PENDING_RECHECK",  # 备用容量不足，排队转待补检
    "RESCHEDULED",      # 设备复役后补检排期
    "DONE",             # 已完成
]

AssignmentStatusText = {
    "ORIGINAL": "原计划",
    "BACKUP": "备用设备",
    "PENDING_RECHECK": "待补检",
    "RESCHEDULED": "已补排",
    "DONE": "已完成",
}
