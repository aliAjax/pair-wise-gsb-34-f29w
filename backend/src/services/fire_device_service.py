from src.constructors.fire_device_factory import build_fire_device_dto
from src.constants.error_messages import REUSE_PAPERWORK_ITEMS, REUSE_PAPERWORK_LABELS
from src.constants.log_templates import LOG_TEMPLATES
from src.repositories.fire_device_repository import FireDeviceRepository
from src.services.audit_service import AuditService
from src.utils.exceptions import ServiceException
from src.utils.formatters import format_paperwork, parse_dt


class FireDeviceService:
    def __init__(self, db):
        self.db = db
        self.repo = FireDeviceRepository(db)
        self.audit = AuditService(db)

    def list(self, building_id=None, status=None, device_type=None):
        rows = self.repo.find_all(building_id=building_id, status=status, device_type=device_type)
        return [build_fire_device_dto(row) for row in rows]

    def get(self, device_id):
        row = self.repo.get(device_id)
        if row is None:
            raise ServiceException("DEVICE_NOT_FOUND", 404, device_id=device_id)
        return build_fire_device_dto(row)

    def create(self, payload, actor):
        if self.repo.get_by_code(payload.device_code) is not None:
            raise ServiceException("VALIDATION_FAILED", 422, detail=f"设备编号 {payload.device_code} 已存在")
        row = self.repo.create(
            building_id=payload.building_id,
            device_code=payload.device_code,
            device_type=payload.device_type,
            floor=payload.floor,
            location_desc=payload.location_desc,
            install_date=parse_dt(payload.install_date),
            next_maintenance_at=parse_dt(payload.next_maintenance_at),
            status="NORMAL",
            reuse_paperwork="",
        )
        self.audit.log_template(
            "FireDevice", 0, actor, row.id,
            device_code=row.device_code, device_type=row.device_type,
        )
        self.db.commit()
        return build_fire_device_dto(row)

    def add_paperwork(self, device_id, payload, actor):
        """登记复役手续（维保商/主管可在复役前逐项补齐）。"""
        row = self.repo.get(device_id)
        if row is None:
            raise ServiceException("DEVICE_NOT_FOUND", 404, device_id=device_id)
        invalid = [item for item in payload.paperwork_items if item not in REUSE_PAPERWORK_ITEMS]
        if invalid:
            raise ServiceException("VALIDATION_FAILED", 422, detail=f"未知手续项 {invalid}")
        existing = {p for p in (row.reuse_paperwork or "").split(",") if p}
        merged = existing | set(payload.paperwork_items)
        row.reuse_paperwork = format_paperwork(merged)
        missing = [item for item in REUSE_PAPERWORK_ITEMS if item not in merged]
        self.audit.log_template(
            "FireDevice", 3, actor, row.id,
            device_code=row.device_code,
            missing="、".join(REUSE_PAPERWORK_LABELS[m] for m in missing) or "无",
        )
        self.db.commit()
        return build_fire_device_dto(row)

    def reactivate(self, device_id, actor):
        """复役：手续没补齐的设备不能回到正常。

        - OUTAGE 停用结束 -> 若手续未齐，转 PENDING_REUSE（待复役）而不是 NORMAL；
        - PENDING_REUSE -> 手续齐了才允许回到 NORMAL。
        """
        row = self.repo.get(device_id)
        if row is None:
            raise ServiceException("DEVICE_NOT_FOUND", 404, device_id=device_id)
        if row.status not in ("OUTAGE", "PENDING_REUSE"):
            raise ServiceException("DEVICE_NOT_OUTAGE", 409, device_id=row.device_code)

        done = {p for p in (row.reuse_paperwork or "").split(",") if p}
        missing = [item for item in REUSE_PAPERWORK_ITEMS if item not in done]

        if missing:
            row.status = "PENDING_REUSE"
            self.db.commit()
            labels = "、".join(REUSE_PAPERWORK_LABELS[m] for m in missing)
            self.db.refresh(row)
            self.audit.log_template(
                "FireDevice", 2, actor, row.id,
                device_code=row.device_code, from_status="OUTAGE", to_status="PENDING_REUSE",
            )
            self.db.commit()
            raise ServiceException(
                "PAPERWORK_INCOMPLETE", 409, device_id=row.device_code, missing=labels,
            )

        previous = row.status
        row.status = "NORMAL"
        self.audit.log_template(
            "FireDevice", 2, actor, row.id,
            device_code=row.device_code, from_status=previous, to_status="NORMAL",
        )
        self.audit.log(
            actor, "DeviceOutage", "DeviceOutage.reuse", row.id,
            detail=LOG_TEMPLATES["DeviceOutage"][5].format(
                device_id=row.device_code, paperwork_status="齐全，恢复正常",
            ),
        )
        self.db.commit()
        return build_fire_device_dto(row)
