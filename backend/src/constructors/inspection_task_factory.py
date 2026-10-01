from src.utils.formatters import to_iso


def build_inspection_task_dto(row):
    return {
        "id": row.id,
        "building_id": row.building_id,
        "inspector_id": row.inspector_id,
        "plan_date": to_iso(row.plan_date),
        "task_type": row.task_type,
        "status": row.status,
        "checklist_version": row.checklist_version,
        "finished_at": to_iso(row.finished_at),
    }
