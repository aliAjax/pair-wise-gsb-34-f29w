from src.constructors.inspection_result_factory import build_inspection_result_dto
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.services.audit_service import AuditService
from src.utils.exceptions import ServiceException


class InspectionResultService:
    def __init__(self, db):
        self.db = db
        self.repo = InspectionResultRepository(db)
        self.task_repo = InspectionTaskRepository(db)
        self.ticket_repo = HazardTicketRepository(db)
        self.audit = AuditService(db)

    def list(self, task_id=None, device_id=None, review_flag=None):
        rows = self.repo.find_all(task_id=task_id, device_id=device_id, review_flag=review_flag)
        return [build_inspection_result_dto(row) for row in rows]

    def create(self, payload, actor):
        if self.task_repo.get(payload.task_id) is None:
            raise ServiceException("TASK_NOT_FOUND", 404, task_id=payload.task_id)
        row = self.repo.create(
            task_id=payload.task_id,
            device_id=payload.device_id,
            item_code=payload.item_code,
            result_status=payload.result_status,
            measured_value=payload.measured_value,
            photo_url=payload.photo_url,
            note=payload.note,
        )
        self.audit.log_template(
            "InspectionResult", 0, actor, row.id,
            task_id=row.task_id, device_id=row.device_id,
        )
        self.db.commit()
        return build_inspection_result_dto(row)

    def review_voided(self, result_id, payload, actor):
        """停用时段变化导致作废后的人工复核：恢复有效或确认作废。"""
        row = self.repo.get(result_id)
        if row is None:
            raise ServiceException("RESULT_NOT_FOUND", 404, result_id=result_id)
        if row.review_flag != "VOID_PENDING_REVIEW":
            raise ServiceException("CONFLICT_STATE", 409)
        if payload.action == "REINSTATE":
            row.review_flag = "ACTIVE"
            row.voided_at = None
            row.voided_by_outage_id = None
        elif payload.action == "CONFIRM_VOID":
            row.review_flag = "VOID_CONFIRMED"
        else:
            raise ServiceException("VALIDATION_FAILED", 422, detail="action 只支持 REINSTATE/CONFIRM_VOID")
        if payload.note:
            row.note = payload.note
        self.audit.log_template(
            "InspectionResult", 2, actor, row.id,
            result_id=row.id, result_status=row.review_flag,
        )
        self.db.commit()
        return build_inspection_result_dto(row)
