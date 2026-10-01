"""容量占用仓储：恢复时按 (window_id, assignment_id) 幂等判重。"""
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.models.capacity_holding import CapacityHolding


class CapacityHoldingRepository:
    def __init__(self, db: Session):
        self.db = db

    def exists(self, window_id: int, assignment_id: int) -> bool:
        return self.db.execute(
            select(CapacityHolding.id).where(
                CapacityHolding.window_id == window_id,
                CapacityHolding.assignment_id == assignment_id,
            ).limit(1)
        ).scalar_one_or_none() is not None

    def hold(self, *, window_id: int, backup_device_id: int,
             assignment_id: int, seats: int) -> CapacityHolding:
        row = CapacityHolding(
            window_id=window_id,
            backup_device_id=backup_device_id,
            assignment_id=assignment_id,
            seats=seats,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def occupied_seats(self, window_id: int) -> int:
        """该停用时段已占用的备用名额总数（断点续跑后不重复计数）。"""
        value = self.db.execute(
            select(func.coalesce(func.sum(CapacityHolding.seats), 0)).where(
                CapacityHolding.window_id == window_id
            )
        ).scalar_one()
        return int(value or 0)

    def occupied_seats_on_device_for_window(self, device_id: int, window_id: int) -> int:
        """指定窗口内，某台备用设备已被占用的名额。"""
        value = self.db.execute(
            select(func.coalesce(func.sum(CapacityHolding.seats), 0)).where(
                CapacityHolding.backup_device_id == device_id,
                CapacityHolding.window_id == window_id,
            )
        ).scalar_one()
        return int(value or 0)

    def list_by_window(self, window_id: int) -> list[CapacityHolding]:
        return list(
            self.db.execute(
                select(CapacityHolding).where(CapacityHolding.window_id == window_id)
            ).scalars().all()
        )
