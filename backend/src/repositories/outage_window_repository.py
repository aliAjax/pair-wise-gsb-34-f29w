"""停用时段 / 草稿 / 手续仓储。"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.device_outage_window import DeviceOutageWindow
from src.models.outage_draft import OutageDraft
from src.models.outage_procedure import OutageProcedure


class DeviceOutageWindowRepository:
    def __init__(self, db: Session):
        self.db = db

    def lock_row(self, window_id: int) -> DeviceOutageWindow | None:
        """SELECT ... FOR UPDATE（PG 行锁）；SQLite 下回退普通查询。"""
        stmt = select(DeviceOutageWindow).where(DeviceOutageWindow.id == window_id)
        if self.db.bind.dialect.name == "postgresql":
            stmt = stmt.with_for_update()
        return self.db.execute(stmt).scalar_one_or_none()

    def get(self, window_id: int) -> DeviceOutageWindow | None:
        return self.db.get(DeviceOutageWindow, window_id)

    def add(self, **fields) -> DeviceOutageWindow:
        row = DeviceOutageWindow(**fields)
        self.db.add(row)
        self.db.flush()
        return row

    def list_by_device(self, device_id: int) -> list[DeviceOutageWindow]:
        stmt = (
            select(DeviceOutageWindow)
            .where(DeviceOutageWindow.device_id == device_id)
            .order_by(DeviceOutageWindow.version.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_confirmed(self) -> list[DeviceOutageWindow]:
        stmt = select(DeviceOutageWindow).where(
            DeviceOutageWindow.outage_status == "CONFIRMED"
        )
        return list(self.db.execute(stmt).scalars().all())

    def latest_group_version(self, group_id: int) -> int:
        stmt = (
            select(DeviceOutageWindow.version)
            .where(DeviceOutageWindow.window_group_id == group_id)
            .order_by(DeviceOutageWindow.version.desc())
            .limit(1)
        )
        value = self.db.execute(stmt).scalar_one_or_none()
        return value or 0

    def max_group_id(self) -> int:
        value = self.db.execute(
            select(func.max(DeviceOutageWindow.window_group_id))
        ).scalar_one_or_none()
        return int(value or 0)


class OutageDraftRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, *, window_id: int, owner_id: int, payload: str,
               observed_occupied: int, lock_version: int) -> OutageDraft:
        row = self.db.execute(
            select(OutageDraft).where(
                OutageDraft.window_id == window_id,
                OutageDraft.owner_id == owner_id,
            )
        ).scalar_one_or_none()
        if row is None:
            row = OutageDraft(
                window_id=window_id,
                owner_id=owner_id,
                payload=payload,
                observed_occupied=observed_occupied,
                lock_version=lock_version,
            )
            self.db.add(row)
        else:
            # 乐观锁：后到者必须基于最新占用数量版本保存草稿。
            if lock_version < row.lock_version:
                from src.utils.exceptions import ServiceError

                raise ServiceError(
                    "OUTAGE_DRAFT_VERSION_STALE", 409, version=row.lock_version
                )
            row.payload = payload
            row.observed_occupied = observed_occupied
            row.lock_version = row.lock_version + 1
        self.db.flush()
        return row

    def list_by_window(self, window_id: int) -> list[OutageDraft]:
        return list(
            self.db.execute(
                select(OutageDraft)
                .where(OutageDraft.window_id == window_id)
                .order_by(OutageDraft.id.asc())
            ).scalars().all()
        )


class OutageProcedureRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, **fields) -> OutageProcedure:
        row = OutageProcedure(**fields)
        self.db.add(row)
        self.db.flush()
        return row

    def list_by_device_window(self, device_id: int, window_id: int) -> list[OutageProcedure]:
        return list(
            self.db.execute(
                select(OutageProcedure).where(
                    OutageProcedure.device_id == device_id,
                    OutageProcedure.window_id == window_id,
                )
            ).scalars().all()
        )

    def list_latest_by_device(self, device_id: int) -> list[OutageProcedure]:
        return list(
            self.db.execute(
                select(OutageProcedure)
                .where(OutageProcedure.device_id == device_id)
                .order_by(OutageProcedure.window_id.desc())
            ).scalars().all()
        )
