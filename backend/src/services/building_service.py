"""建筑楼栋业务服务。"""
from src.constructors.building_factory import create_building_dto
from src.repositories.building_repository import BuildingRepository
from src.services.audit_service import AuditService
from src.types.building_payload import BuildingCreatePayload


class BuildingService:
    def __init__(self, db):
        self.db = db
        self.repo = BuildingRepository(db)
        self.audit = AuditService(db)

    def list(self):
        return [create_building_dto(row) for row in self.repo.find_all()]

    def create(self, payload: BuildingCreatePayload, actor: str = "system"):
        row = self.repo.add(**payload.model_dump())
        self.audit.log(
            "Building", 0, actor=actor, target_id=row.id,
            name=row.name, campus=row.campus,
        )
        self.db.commit()
        return create_building_dto(row)
