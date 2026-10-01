"""建筑楼栋数据访问层。"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.building import Building


class BuildingRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[Building]:
        return list(self.db.execute(select(Building).order_by(Building.id.asc())).scalars().all())

    def get(self, building_id: int) -> Building | None:
        return self.db.get(Building, building_id)

    def add(self, **fields) -> Building:
        row = Building(**fields)
        self.db.add(row)
        self.db.flush()
        return row
