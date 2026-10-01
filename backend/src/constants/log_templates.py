# 日志模板集中存放，每个实体至少 4 条；所有写操作都要落审计日志。
# 字段变更时必须同步改这里和 service 中的调用处。
LOG_TEMPLATES = {
    "Building": [
        "Building.create 楼栋建档：{name}（{campus}）",
        "Building.update 楼栋资料变更：{name} 字段 {fields}",
        "Building.manager 楼栋责任人维护：{name} -> {manager_id}",
        "Building.export 楼栋台账导出：操作者 {actor}",
    ],
    "FireDevice": [
        "FireDevice.create 设备登记：{device_code} 类型 {device_type}",
        "FireDevice.update 设备资料变更：{device_code} 字段 {fields}",
        "FireDevice.status 设备状态变更：{device_code} {from_status} -> {to_status}",
        "FireDevice.paperwork 设备复役手续登记：{device_code} 缺 {missing}",
    ],
    "InspectionTask": [
        "InspectionTask.create 巡检排期：{plan_date} 类型 {task_type}",
        "InspectionTask.update 巡检任务变更：#{task_id} 字段 {fields}",
        "InspectionTask.status 巡检任务状态：#{task_id} {from_status} -> {to_status}",
        "InspectionTask.reroute 停用冲突改派：#{task_id} 原设备 {from_device_id} -> 备用 {to_device_id}",
        "InspectionTask.makeup 备用容量不足排队待补检：#{task_id} 设备 {device_id}",
    ],
    "InspectionResult": [
        "InspectionResult.create 检查项录入：任务 #{task_id} 设备 {device_id}",
        "InspectionResult.update 检查结果变更：#{result_id} 字段 {fields}",
        "InspectionResult.status 检查结果判定：#{result_id} -> {result_status}",
        "InspectionResult.void 停用时段变化，检查结果作废待复核：#{result_id}",
    ],
    "HazardTicket": [
        "HazardTicket.create 异常触发隐患单：结果 #{result_id} 等级 {severity}",
        "HazardTicket.dispatch 隐患派单：#{ticket_id} -> 责任人 {owner_id}",
        "HazardTicket.rectify 整改回填：#{ticket_id} 状态 {rectify_status}",
        "HazardTicket.void 停用时段变化，隐患整改单作废待复核：#{ticket_id}",
        "HazardTicket.close 复验关闭：#{ticket_id}",
    ],
    "DeviceOutage": [
        "DeviceOutage.submit 提交停用时段：设备 {device_id} {start_at}~{end_at}",
        "DeviceOutage.confirm 确认停用时段：#{outage_id} 占用名额 {occupied_count}",
        "DeviceOutage.draft 冲突保留草稿：#{outage_id} 占用数量 {occupied_count}",
        "DeviceOutage.change 停用时段变更：#{outage_id} 触发 {voided_count} 条记录作废",
        "DeviceOutage.resume 失败续传：批次 #{batch_id} 恢复 {resumed_count} 台设备",
        "DeviceOutage.reuse 复役校验：设备 {device_id} 手续 {paperwork_status}",
    ],
}
