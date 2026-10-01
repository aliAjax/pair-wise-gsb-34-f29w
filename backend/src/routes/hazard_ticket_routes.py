from fastapi import APIRouter

from src.controllers.hazard_ticket_controller import (
    create_hazard_ticket,
    dispatch_hazard_ticket,
    list_hazard_ticket,
    rectify_hazard_ticket,
    review_or_close_hazard_ticket,
)

router = APIRouter(prefix="/api/hazard-ticket", tags=["HazardTicket"])
router.get("", response_model=None)(list_hazard_ticket)
router.post("", response_model=None)(create_hazard_ticket)
router.post("/{ticket_id}/dispatch", response_model=None)(dispatch_hazard_ticket)
router.post("/{ticket_id}/rectify", response_model=None)(rectify_hazard_ticket)
router.post("/{ticket_id}/review", response_model=None)(review_or_close_hazard_ticket)
