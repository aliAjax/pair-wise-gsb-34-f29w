from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.controllers.base_controller import call
from src.middlewares.rbac_middleware import require_roles
from src.services.inspection_task_service import InspectionTaskService
from src.types.inspection_task_payload import InspectionTaskPayload, TaskStatusPayload


def list_inspection_task(
    status: str | None = None,
    building_id: int | None = None,
    db: Session = Depends(get_db),
):
    return InspectionTaskService(db).list(status=status, building_id=building_id)


def get_inspection_task(task_id: int, db: Session = Depends(get_db)):
    return call(InspectionTaskService(db).get, task_id)


def create_inspection_task(
    payload: InspectionTaskPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("SUPERVISOR", "INSPECTOR")),
):
    return call(InspectionTaskService(db).create, payload, actor=user["id"])


def change_inspection_task_status(
    task_id: int,
    payload: TaskStatusPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("INSPECTOR", "SUPERVISOR")),
):
    return call(InspectionTaskService(db).change_status, task_id, payload, actor=user["id"])
