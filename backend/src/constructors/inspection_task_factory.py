"""巡检任务响应构造器：ORM -> DTO。"""


def create_inspection_task_dto(row, **overrides):
    data = {
        "id": row.id,
        "building_id": row.building_id,
        "inspector_id": row.inspector_id,
        "plan_date": row.plan_date.isoformat() if getattr(row, "plan_date", None) else None,
        "task_type": row.task_type,
        "status": row.status,
        "checklist_version": row.checklist_version,
        "finished_at": row.finished_at.isoformat() if getattr(row, "finished_at", None) else None,
    }
    data.update(overrides)
    return data
