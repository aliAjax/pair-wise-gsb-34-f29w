"""停用时段 / 排期 / 占用 / 手续 响应构造器。"""


def create_outage_window_dto(row, **overrides):
    data = {
        "id": row.id,
        "window_group_id": row.window_group_id,
        "version": row.version,
        "device_id": row.device_id,
        "owner_id": row.owner_id,
        "start_at": row.start_at.isoformat() if row.start_at else None,
        "end_at": row.end_at.isoformat() if row.end_at else None,
        "reason": row.reason,
        "outage_status": row.outage_status,
        "occupied_capacity": row.occupied_capacity,
        "demanded_capacity": row.demanded_capacity,
        "write_stage": row.write_stage,
        "resume_key": row.resume_key,
        "last_error": row.last_error,
        "confirmed_at": row.confirmed_at.isoformat() if row.confirmed_at else None,
    }
    data.update(overrides)
    return data


def create_assignment_dto(row, **overrides):
    data = {
        "id": row.id,
        "task_id": row.task_id,
        "building_id": row.building_id,
        "device_type": row.device_type,
        "planned_device_id": row.planned_device_id,
        "actual_device_id": row.actual_device_id,
        "assignment_status": row.assignment_status,
        "window_id": row.window_id,
        "origin_assignment_id": row.origin_assignment_id,
        "queue_position": row.queue_position,
        "seats": row.seats,
    }
    data.update(overrides)
    return data


def create_holding_dto(row, **overrides):
    data = {
        "id": row.id,
        "window_id": row.window_id,
        "backup_device_id": row.backup_device_id,
        "assignment_id": row.assignment_id,
        "seats": row.seats,
    }
    data.update(overrides)
    return data


def create_procedure_dto(row, **overrides):
    data = {
        "id": row.id,
        "device_id": row.device_id,
        "window_id": row.window_id,
        "procedure_type": row.procedure_type,
        "completed": bool(row.completed),
        "doc_url": row.doc_url,
    }
    data.update(overrides)
    return data


def create_draft_dto(row, **overrides):
    data = {
        "id": row.id,
        "window_id": row.window_id,
        "owner_id": row.owner_id,
        "payload": row.payload,
        "observed_occupied": row.observed_occupied,
        "lock_version": row.lock_version,
    }
    data.update(overrides)
    return data
