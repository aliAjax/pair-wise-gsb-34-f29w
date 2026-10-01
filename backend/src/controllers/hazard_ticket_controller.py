from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.controllers.base_controller import call
from src.middlewares.rbac_middleware import require_roles
from src.services.hazard_ticket_service import HazardTicketService
from src.types.hazard_ticket_payload import (
    HazardTicketPayload,
    RectifyTicketPayload,
    ReviewTicketPayload,
)


def list_hazard_ticket(
    rectify_status: str | None = None,
    device_id: int | None = None,
    db: Session = Depends(get_db),
):
    return HazardTicketService(db).list(rectify_status=rectify_status, device_id=device_id)


def create_hazard_ticket(
    payload: HazardTicketPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("INSPECTOR", "SUPERVISOR")),
):
    return call(HazardTicketService(db).create, payload, actor=user["id"])


def dispatch_hazard_ticket(
    ticket_id: int,
    owner_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("SUPERVISOR")),
):
    return call(HazardTicketService(db).dispatch, ticket_id, owner_id, actor=user["id"])


def rectify_hazard_ticket(
    ticket_id: int,
    payload: RectifyTicketPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("MAINTAINER", "SUPERVISOR")),
):
    return call(HazardTicketService(db).rectify, ticket_id, payload, actor=user["id"])


def review_or_close_hazard_ticket(
    ticket_id: int,
    payload: ReviewTicketPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("SUPERVISOR", "AUDITOR")),
):
    return call(HazardTicketService(db).review_or_close, ticket_id, payload, actor=user["id"])
