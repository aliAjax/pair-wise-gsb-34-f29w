"""隐患整改单响应构造器：ORM -> DTO，携带作废待复核状态。"""


def create_hazard_ticket_dto(row, **overrides):
    data = {
        "id": row.id,
        "result_id": row.result_id,
        "severity": row.severity,
        "owner_id": row.owner_id,
        "deadline": row.deadline.isoformat() if getattr(row, "deadline", None) else None,
        "rectify_status": row.rectify_status,
        "rectify_note": row.rectify_note,
        "closed_at": row.closed_at.isoformat() if getattr(row, "closed_at", None) else None,
        "review_status": getattr(row, "review_status", "ACTIVE"),
        "voided_by_window_id": getattr(row, "voided_by_window_id", None),
        "reviewed_at": row.reviewed_at.isoformat() if getattr(row, "reviewed_at", None) else None,
    }
    data.update(overrides)
    return data
