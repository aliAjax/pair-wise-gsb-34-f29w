"""消防设备数据访问层：含备用容量统计。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.fire_device import FireDevice


class FireDeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[FireDevice]:
        return list(self.db.execute(select(FireDevice).order_by(FireDevice.id.asc())).scalars().all())

    def get(self, device_id: int) -> FireDevice | None:
        return self.db.get(FireDevice, device_id)

    def list_by_ids(self, device_ids: list[int]) -> list[FireDevice]:
        if not device_ids:
            return []
        return list(
            self.db.execute(
                select(FireDevice).where(FireDevice.id.in_(device_ids))
            ).scalars().all()
        )

    def list_backup_candidates(
        self, *, building_id: int, device_type: str, exclude_device_ids: list[int],
    ) -> list[FireDevice]:
        """同栋同类型、当前正常、且不在停用集合内的备用设备。"""
        stmt = select(FireDevice).where(
            FireDevice.building_id == building_id,
            FireDevice.device_type == device_type,
            FireDevice.status == "NORMAL",
        )
        if exclude_device_ids:
            stmt = stmt.where(FireDevice.id.notin_(exclude_device_ids))
        return list(
            self.db.execute(stmt.order_by(FireDevice.id.asc())).scalars().all()
        )

    def total_backup_capacity(
        self, *, building_id: int, device_type: str, exclude_device_ids: list[int],
    ) -> int:
        return sum(
            d.capacity for d in self.list_backup_candidates(
                building_id=building_id,
                device_type=device_type,
                exclude_device_ids=exclude_device_ids,
            )
        )

    def add(self, **fields) -> FireDevice:
        row = FireDevice(**fields)
        self.db.add(row)
        self.db.flush()
        return row

    def update_status(self, device_id: int, status: str) -> FireDevice | None:
        row = self.get(device_id)
        if row is not None:
            row.status = status
            self.db.flush()
        return row
