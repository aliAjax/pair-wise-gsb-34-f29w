"""巡检结果数据访问层：支持停用变更触发的作废待复核。"""
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.models.inspection_result import InspectionResult


class InspectionResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[InspectionResult]:
        return list(self.db.execute(select(InspectionResult).order_by(InspectionResult.id.asc())).scalars().all())

    def get(self, result_id: int) -> InspectionResult | None:
        return self.db.get(InspectionResult, result_id)

    def list_by_device(self, device_id: int) -> list[InspectionResult]:
        return list(
            self.db.execute(
                select(InspectionResult).where(InspectionResult.device_id == device_id)
            ).scalars().all()
        )

    def list_by_devices(self, device_ids: list[int]) -> list[InspectionResult]:
        if not device_ids:
            return []
        return list(
            self.db.execute(
                select(InspectionResult).where(InspectionResult.device_id.in_(device_ids))
            ).scalars().all()
        )

    def mark_void_pending(self, *, result_ids: list[int], window_id: int) -> int:
        if not result_ids:
            return 0
        self.db.execute(
            update(InspectionResult)
            .where(InspectionResult.id.in_(result_ids))
            .values(review_status="VOID_PENDING", voided_by_window_id=window_id)
        )
        self.db.flush()
        return len(result_ids)

    def mark_reviewed(self, result_id: int, review_status: str) -> InspectionResult | None:
        row = self.get(result_id)
        if row is not None:
            row.review_status = review_status
            row.reviewed_at = datetime.utcnow()
            self.db.flush()
        return row

    def add(self, **fields) -> InspectionResult:
        row = InspectionResult(**fields)
        self.db.add(row)
        self.db.flush()
        return row
