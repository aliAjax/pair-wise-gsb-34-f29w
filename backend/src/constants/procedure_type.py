"""复役前必须补齐的手续类型。手续不齐的设备不能回到正常。"""

ProcedureType = [
    "MAINTENANCE_REPORT",  # 保养完工报告
    "ACCEPTANCE_CHECK",    # 验收检测
    "SAFETY_SIGN_OFF",     # 安全责任人签收
]

ProcedureTypeText = {
    "MAINTENANCE_REPORT": "保养完工报告",
    "ACCEPTANCE_CHECK": "验收检测",
    "SAFETY_SIGN_OFF": "安全责任人签收",
}
