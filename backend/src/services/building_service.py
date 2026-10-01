from src.constructors.building_factory import build_building_dto
from src.repositories.building_repository import BuildingRepository
from src.services.audit_service import AuditService
from src.utils.exceptions import ServiceException


class BuildingService:
    def __init__(self, db):
        self.db = db
        self.repo = BuildingRepository(db)
        self.audit = AuditService(db)

    def list(self):
        return [build_building_dto(row) for row in self.repo.find_all()]

    def create(self, payload, actor):
        if not payload.name or not payload.campus:
            raise ServiceException("VALIDATION_FAILED", 422, detail="名称与园区必填")
        row = self.repo.create(
            name=payload.name,
            campus=payload.campus,
            floor_count=payload.floor_count,
            fire_grade=payload.fire_grade,
            manager_id=payload.manager_id,
            address_code=payload.address_code,
        )
        self.audit.log_template("Building", 0, actor, row.id, name=row.name, campus=row.campus)
        self.db.commit()
        return build_building_dto(row)
