from src.utils.formatters import to_iso


def build_device_outage_dto(row):
    return {
        "id": row.id,
        "batch_id": row.batch_id,
        "device_id": row.device_id,
        "start_at": to_iso(row.start_at),
        "end_at": to_iso(row.end_at),
        "reason": row.reason,
        "status": row.status,
        "version": row.version,
        "confirmed_by": row.confirmed_by,
        "confirmed_at": to_iso(row.confirmed_at),
        "occupied_count": row.occupied_count,
        "conflict_outage_ids": [int(x) for x in (row.conflict_outage_ids or "").split(",") if x],
    }


def build_outage_batch_dto(row, items=None):
    return {
        "id": row.id,
        "submitted_by": row.submitted_by,
        "submitted_at": to_iso(row.submitted_at),
        "status": row.status,
        "note": row.note,
        "fail_device_codes": [x for x in (row.fail_device_codes or "").split(",") if x],
        "items": items or [],
    }
