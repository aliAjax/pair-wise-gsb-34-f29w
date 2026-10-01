"""审计日志模板集中存放。

每个实体至少 4 条；新增字段 / 动作时必须同步：
constants/log_templates.py -> service 调用处 -> 前端 constants/logTemplates.ts
"""

LOG_TEMPLATES = {
    "Building": [
        "楼栋建档：{name}（{campus}）",
        "楼栋更新：{name} 变更字段 {fields}",
        "楼栋责任人变更：{name} -> 责任人 #{manager_id}",
        "楼栋台账导出：操作人 #{actor_id}",
    ],
    "FireDevice": [
        "设备登记：{device_code}（{device_type}）入册 {building_id}",
        "设备更新：{device_code} 变更字段 {fields}",
        "设备状态变更：{device_code} {from_status} -> {to_status}",
        "设备台账导出：操作人 #{actor_id}",
        "设备提交停用时段：{device_code} {start_at} ~ {end_at}（{outage_status}）",
        "设备复役：{device_code} 由停用恢复为正常，手续 {procedures}",
    ],
    "InspectionTask": [
        "巡检任务创建：#{task_id} 楼栋 {building_id} 计划日期 {plan_date}",
        "巡检任务更新：#{task_id} 变更字段 {fields}",
        "巡检任务状态变更：#{task_id} {from_status} -> {to_status}",
        "巡检任务导出：操作人 #{actor_id}",
        "停用重排：任务 #{task_id} 原设备 #{from_device_id} 改用备用设备 #{to_device_id}",
        "容量排队：任务 #{task_id} 设备 #{device_id} 因备用容量不足转为待补检",
        "补检排期：任务 #{task_id} 待补检项 #{assignment_id} 重排至设备 #{device_id}",
    ],
    "InspectionResult": [
        "巡检结果录入：任务 #{task_id} 设备 #{device_id} 检查项 {item_code} = {result_status}",
        "巡检结果更新：#{result_id} 变更字段 {fields}",
        "巡检结果作废：#{result_id} 因设备 #{device_id} 停用时段变更，待复核",
        "巡检结果复核：#{result_id} 复核结论 {review_status}",
    ],
    "HazardTicket": [
        "隐患派单：#{ticket_id} 来自结果 #{result_id} 等级 {severity}",
        "隐患整改：#{ticket_id} 进展 {rectify_status} 备注 {rectify_note}",
        "隐患整改单作废：#{ticket_id} 因关联设备停用时段变更，待复核",
        "隐患复验关闭：#{ticket_id} 关闭人 #{actor_id}",
        "隐患复核：#{ticket_id} 复核结论 {review_status}",
    ],
    "DeviceOutageWindow": [
        "停用时段草稿：设备 #{device_id} {start_at} ~ {end_at} 负责人 #{owner_id}",
        "停用时段确认：#{window_id} 设备 #{device_id} 占用备用容量 {occupied}",
        "停用占用冲突：#{window_id} 已有占用 {occupied}，需求 {demanded}，草稿已保留",
        "停用写入失败：#{window_id} 阶段 {stage} 原因 {reason}",
        "停用写入恢复：#{window_id} 从阶段 {stage} 续跑成功",
        "停用时段变更：旧版 #{window_id} 被新版 #{new_window_id} 替代",
        "停用手续登记：设备 #{device_id} 手续 {procedure_type}",
    ],
}
