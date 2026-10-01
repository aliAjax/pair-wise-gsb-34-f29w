from src.utils.formatters import to_iso


def build_hazard_ticket_dto(row):
    return {
        "id": row.id,
        "result_id": row.result_id,
        "device_id": row.device_id,
        "severity": row.severity,
        "owner_id": row.owner_id,
        "deadline": to_iso(row.deadline),
        "rectify_status": row.rectify_status,
        "rectify_note": row.rectify_note,
        "closed_at": to_iso(row.closed_at),
        "voided_at": to_iso(row.voided_at),
        "voided_by_outage_id": row.voided_by_outage_id,
    }
