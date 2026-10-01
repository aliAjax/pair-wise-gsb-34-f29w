def build_task_reroute_dto(row):
    return {
        "id": row.id,
        "task_id": row.task_id,
        "outage_id": row.outage_id,
        "device_id": row.device_id,
        "backup_device_id": row.backup_device_id,
        "relation": row.relation,
        "note": row.note,
    }
