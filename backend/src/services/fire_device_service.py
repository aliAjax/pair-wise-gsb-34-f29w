"""消防设备业务服务。"""
from src.constructors.fire_device_factory import create_fire_device_dto
from src.repositories.fire_device_repository import FireDeviceRepository
from src.services.audit_service import AuditService
from src.types.fire_device_payload import FireDeviceCreatePayload
from src.utils.exceptions import ServiceError


class FireDeviceService:
    def __init__(self, db):
        self.db = db
        self.repo = FireDeviceRepository(db)
        self.audit = AuditService(db)

    def list(self):
        return [create_fire_device_dto(row) for row in self.repo.find_all()]

    def get_dto(self, device_id: int):
        row = self.repo.get(device_id)
        if row is None:
            raise ServiceError("NOT_FOUND", 404, resource="消防设备", entity_id=device_id)
        return create_fire_device_dto(row)

    def create(self, payload: FireDeviceCreatePayload, actor: str = "system"):
        data = payload.model_dump()
        install_date = data.pop("install_date", None)
        next_at = data.pop("next_maintenance_at", None)
        row = self.repo.add(
            **data, install_date=install_date, next_maintenance_at=next_at,
            status="NORMAL",
        )
        self.audit.log(
            "FireDevice", 0, actor=actor, target_id=row.id,
            device_code=row.device_code, device_type=row.device_type,
            building_id=row.building_id,
        )
        self.db.commit()
        return create_fire_device_dto(row)
