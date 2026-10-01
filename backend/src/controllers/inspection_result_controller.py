from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.controllers.base_controller import call
from src.middlewares.rbac_middleware import require_roles
from src.services.inspection_result_service import InspectionResultService
from src.types.inspection_result_payload import InspectionResultPayload, ReviewResultPayload


def list_inspection_result(
    task_id: int | None = None,
    device_id: int | None = None,
    review_flag: str | None = None,
    db: Session = Depends(get_db),
):
    return InspectionResultService(db).list(task_id=task_id, device_id=device_id, review_flag=review_flag)


def create_inspection_result(
    payload: InspectionResultPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("INSPECTOR", "SUPERVISOR")),
):
    return call(InspectionResultService(db).create, payload, actor=user["id"])


def review_voided_result(
    result_id: int,
    payload: ReviewResultPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("SUPERVISOR", "AUDITOR")),
):
    return call(InspectionResultService(db).review_voided, result_id, payload, actor=user["id"])
