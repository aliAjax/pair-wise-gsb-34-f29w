"""隐患整改单 DTO。"""
from datetime import datetime

from pydantic import BaseModel


class HazardTicketCreatePayload(BaseModel):
    result_id: int
    severity: str = "MEDIUM"
    owner_id: int | None = None
    deadline: datetime | None = None
    rectify_note: str | None = None


class HazardTicketReviewPayload(BaseModel):
    review_status: str  # RECONFIRMED / REJECTED
