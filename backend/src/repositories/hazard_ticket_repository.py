"""隐患整改单数据访问层：随引用设备停用变更而作废待复核。"""
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.models.hazard_ticket import HazardTicket


class HazardTicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[HazardTicket]:
        return list(self.db.execute(select(HazardTicket).order_by(HazardTicket.id.asc())).scalars().all())

    def get(self, ticket_id: int) -> HazardTicket | None:
        return self.db.get(HazardTicket, ticket_id)

    def list_by_result_ids(self, result_ids: list[int]) -> list[HazardTicket]:
        if not result_ids:
            return []
        return list(
            self.db.execute(
                select(HazardTicket).where(HazardTicket.result_id.in_(result_ids))
            ).scalars().all()
        )

    def mark_void_pending(self, *, ticket_ids: list[int], window_id: int) -> int:
        if not ticket_ids:
            return 0
        self.db.execute(
            update(HazardTicket)
            .where(HazardTicket.id.in_(ticket_ids))
            .values(review_status="VOID_PENDING", voided_by_window_id=window_id)
        )
        self.db.flush()
        return len(ticket_ids)

    def mark_reviewed(self, ticket_id: int, review_status: str) -> HazardTicket | None:
        row = self.get(ticket_id)
        if row is not None:
            row.review_status = review_status
            row.reviewed_at = datetime.utcnow()
            self.db.flush()
        return row

    def add(self, **fields) -> HazardTicket:
        row = HazardTicket(**fields)
        self.db.add(row)
        self.db.flush()
        return row
