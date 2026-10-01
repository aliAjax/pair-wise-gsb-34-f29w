"""隐患整改单控制器：含作废待复核的复核动作。"""
from fastapi import Depends, Request

from src.database import get_db
from src.services.hazard_ticket_service import HazardTicketService
from src.types.hazard_ticket_payload import (
    HazardTicketCreatePayload,
    HazardTicketReviewPayload,
)


def _actor(request: Request) -> str:
    return str((getattr(request.state, "user", None) or {}).get("id", "system"))


def list_hazard_ticket(request: Request, db=Depends(get_db)):
    return HazardTicketService(db).list()


def create_hazard_ticket(payload: HazardTicketCreatePayload, request: Request,
                         db=Depends(get_db)):
    return HazardTicketService(db).create(payload, actor=_actor(request))


def review_hazard_ticket(ticket_id: int, payload: HazardTicketReviewPayload,
                         request: Request, db=Depends(get_db)):
    return HazardTicketService(db).review(
        ticket_id, payload.review_status, actor=_actor(request)
    )
