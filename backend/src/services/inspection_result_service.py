"""巡检结果业务服务。"""
from src.constructors.inspection_result_factory import create_inspection_result_dto
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.services.audit_service import AuditService
from src.types.inspection_result_payload import InspectionResultCreatePayload
from src.utils.exceptions import ServiceError


class InspectionResultService:
    def __init__(self, db):
        self.db = db
        self.repo = InspectionResultRepository(db)
        self.audit = AuditService(db)

    def list(self):
        return [create_inspection_result_dto(row) for row in self.repo.find_all()]

    def create(self, payload: InspectionResultCreatePayload, actor: str = "system"):
        row = self.repo.add(**payload.model_dump(), review_status="ACTIVE")
        self.audit.log(
            "InspectionResult", 0, actor=actor, target_id=row.id,
            task_id=row.task_id, device_id=row.device_id,
            item_code=row.item_code, result_status=row.result_status,
        )
        self.db.commit()
        return create_inspection_result_dto(row)

    def review(self, result_id: int, review_status: str, actor: str = "system"):
        if review_status not in ("RECONFIRMED", "REJECTED"):
            raise ServiceError("VALIDATION_FAILED", 400, detail="review_status 非法")
        row = self.repo.mark_reviewed(result_id, review_status)
        if row is None:
            raise ServiceError("REVIEW_RECORD_NOT_FOUND", 404,
                               record_type="InspectionResult", record_id=result_id)
        self.audit.log(
            "InspectionResult", 3, actor=actor, target_id=result_id,
            result_id=result_id, review_status=review_status,
        )
        self.db.commit()
        return create_inspection_result_dto(row)
