"""停用确认写入流程的阶段标记，用于写入失败后的断点续跑（恢复）。

每个阶段都必须幂等：已占用名额不重复、不丢失。
"""

WriteStage = [
    "PERSIST_WINDOW",       # 停用时段落库（草稿 -> 已确认）
    "HOLD_CAPACITY",        # 占用备用容量名额
    "REALLOCATE_TASKS",     # 同段巡检改用备用设备 / 排队转待补检
    "MARK_DEVICE_OUTAGE",   # 设备状态置为停用
    "COMPLETED",            # 全部完成
]

WriteStageText = {
    "PERSIST_WINDOW": "停用时段落库",
    "HOLD_CAPACITY": "占用备用容量",
    "REALLOCATE_TASKS": "巡检任务重排",
    "MARK_DEVICE_OUTAGE": "设备置为停用",
    "COMPLETED": "确认完成",
}
