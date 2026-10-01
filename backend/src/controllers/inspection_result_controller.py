"""巡检结果控制器：含作废待复核的复核动作。"""
from fastapi import Depends, Request

from src.database import get_db
from src.services.inspection_result_service import InspectionResultService
from src.types.hazard_ticket_payload import HazardTicketReviewPayload
from src.types.inspection_result_payload import InspectionResultCreatePayload


def _actor(request: Request) -> str:
    return str((getattr(request.state, "user", None) or {}).get("id", "system"))


def list_inspection_result(request: Request, db=Depends(get_db)):
    return InspectionResultService(db).list()


def create_inspection_result(payload: InspectionResultCreatePayload, request: Request,
                             db=Depends(get_db)):
    return InspectionResultService(db).create(payload, actor=_actor(request))


def review_inspection_result(result_id: int, payload: HazardTicketReviewPayload,
                             request: Request, db=Depends(get_db)):
    return InspectionResultService(db).review(
        result_id, payload.review_status, actor=_actor(request)
    )
