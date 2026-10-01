"""隐患整改单业务服务。"""
from src.constructors.hazard_ticket_factory import create_hazard_ticket_dto
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.services.audit_service import AuditService
from src.types.hazard_ticket_payload import HazardTicketCreatePayload
from src.utils.exceptions import ServiceError


class HazardTicketService:
    def __init__(self, db):
        self.db = db
        self.repo = HazardTicketRepository(db)
        self.result_repo = InspectionResultRepository(db)
        self.audit = AuditService(db)

    def list(self):
        return [create_hazard_ticket_dto(row) for row in self.repo.find_all()]

    def create(self, payload: HazardTicketCreatePayload, actor: str = "system"):
        result = self.result_repo.get(payload.result_id)
        if result is None:
            raise ServiceError("NOT_FOUND", 404, resource="巡检结果",
                               entity_id=payload.result_id)
        data = payload.model_dump()
        row = self.repo.add(
            result_id=data["result_id"],
            severity=data["severity"],
            owner_id=data.get("owner_id"),
            deadline=data.get("deadline"),
            rectify_note=data.get("rectify_note"),
            rectify_status="OPEN",
            review_status="ACTIVE",
        )
        self.audit.log(
            "HazardTicket", 0, actor=actor, target_id=row.id,
            ticket_id=row.id, result_id=row.result_id, severity=row.severity,
        )
        self.db.commit()
        return create_hazard_ticket_dto(row)

    def review(self, ticket_id: int, review_status: str, actor: str = "system"):
        if review_status not in ("RECONFIRMED", "REJECTED"):
            raise ServiceError("VALIDATION_FAILED", 400, detail="review_status 非法")
        row = self.repo.mark_reviewed(ticket_id, review_status)
        if row is None:
            raise ServiceError("REVIEW_RECORD_NOT_FOUND", 404,
                               record_type="HazardTicket", record_id=ticket_id)
        self.audit.log(
            "HazardTicket", 4, actor=actor, target_id=ticket_id,
            ticket_id=ticket_id, review_status=review_status,
        )
        self.db.commit()
        return create_hazard_ticket_dto(row)
