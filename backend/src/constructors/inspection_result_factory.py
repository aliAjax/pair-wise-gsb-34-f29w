from src.utils.formatters import to_iso


def build_inspection_result_dto(row):
    return {
        "id": row.id,
        "task_id": row.task_id,
        "device_id": row.device_id,
        "item_code": row.item_code,
        "result_status": row.result_status,
        "measured_value": row.measured_value,
        "photo_url": row.photo_url,
        "note": row.note,
        "review_flag": row.review_flag,
        "voided_at": to_iso(row.voided_at),
        "voided_by_outage_id": row.voided_by_outage_id,
    }
