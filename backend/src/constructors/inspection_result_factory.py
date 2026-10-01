"""巡检结果响应构造器：ORM -> DTO，携带作废待复核状态。"""


def create_inspection_result_dto(row, **overrides):
    data = {
        "id": row.id,
        "task_id": row.task_id,
        "device_id": row.device_id,
        "item_code": row.item_code,
        "result_status": row.result_status,
        "measured_value": row.measured_value,
        "photo_url": row.photo_url,
        "note": row.note,
        "review_status": getattr(row, "review_status", "ACTIVE"),
        "voided_by_window_id": getattr(row, "voided_by_window_id", None),
        "reviewed_at": row.reviewed_at.isoformat() if getattr(row, "reviewed_at", None) else None,
    }
    data.update(overrides)
    return data
