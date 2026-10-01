"""巡检任务控制器。"""
from fastapi import Depends, Request

from src.database import get_db
from src.services.inspection_task_service import InspectionTaskService
from src.types.inspection_task_payload import InspectionTaskCreatePayload


def _actor(request: Request) -> str:
    return str((getattr(request.state, "user", None) or {}).get("id", "system"))


def list_inspection_task(request: Request, db=Depends(get_db)):
    return InspectionTaskService(db).list()


def list_assignments(request: Request, task_id: int | None = None,
                     db=Depends(get_db)):
    return InspectionTaskService(db).list_assignments(task_id)


def create_inspection_task(payload: InspectionTaskCreatePayload, request: Request,
                           db=Depends(get_db)):
    return InspectionTaskService(db).create(payload, actor=_actor(request))
