from datetime import datetime, timezone

from src.constructors.hazard_ticket_factory import build_hazard_ticket_dto
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.services.audit_service import AuditService
from src.utils.exceptions import ServiceException
from src.utils.formatters import parse_dt


class HazardTicketService:
    def __init__(self, db):
        self.db = db
        self.repo = HazardTicketRepository(db)
        self.result_repo = InspectionResultRepository(db)
        self.device_repo = FireDeviceRepository(db)
        self.audit = AuditService(db)

    def list(self, rectify_status=None, device_id=None):
        rows = self.repo.find_all(rectify_status=rectify_status, device_id=device_id)
        return [build_hazard_ticket_dto(row) for row in rows]

    def create(self, payload, actor):
        result = self.result_repo.get(payload.result_id)
        if result is None:
            raise ServiceException("RESULT_NOT_FOUND", 404, result_id=payload.result_id)
        if result.result_status != "ABNORMAL":
            raise ServiceException("VALIDATION_FAILED", 422, detail="只有异常结果才能开隐患单")
        if self.repo.get_by_result(payload.result_id) is not None:
            raise ServiceException("VALIDATION_FAILED", 422, detail="该结果已开单")
        row = self.repo.create(
            result_id=payload.result_id,
            device_id=result.device_id,
            severity=payload.severity,
            owner_id=payload.owner_id,
            deadline=parse_dt(payload.deadline),
            rectify_status="OPEN",
        )
        self.audit.log_template(
            "HazardTicket", 0, actor, row.id,
            result_id=row.result_id, severity=row.severity,
        )
        self.db.commit()
        return build_hazard_ticket_dto(row)

    def dispatch(self, ticket_id, owner_id, actor):
        row = self.repo.get(ticket_id)
        if row is None:
            raise ServiceException("TICKET_NOT_FOUND", 404, ticket_id=ticket_id)
        row.owner_id = owner_id
        if row.rectify_status == "OPEN":
            row.rectify_status = "ASSIGNED"
        self.audit.log_template("HazardTicket", 1, actor, row.id, ticket_id=row.id, owner_id=owner_id)
        self.db.commit()
        return build_hazard_ticket_dto(row)

    def rectify(self, ticket_id, payload, actor):
        row = self.repo.get(ticket_id)
        if row is None:
            raise ServiceException("TICKET_NOT_FOUND", 404, ticket_id=ticket_id)
        row.rectify_note = payload.rectify_note
        if row.rectify_status not in ("VOID_PENDING_REVIEW",):
            row.rectify_status = "RECTIFIED"
        self.audit.log_template(
            "HazardTicket", 2, actor, row.id, ticket_id=row.id, rectify_status=row.rectify_status,
        )
        self.db.commit()
        return build_hazard_ticket_dto(row)

    def review_or_close(self, ticket_id, payload, actor):
        """停用时段变化作废后的复核，或整改完成后的复验关闭。"""
        row = self.repo.get(ticket_id)
        if row is None:
            raise ServiceException("TICKET_NOT_FOUND", 404, ticket_id=ticket_id)
        if payload.action == "REINSTATE":
            row.rectify_status = "ASSIGNED" if row.owner_id else "OPEN"
            row.voided_at = None
            row.voided_by_outage_id = None
        elif payload.action == "CONFIRM_VOID":
            row.rectify_status = "VOID_CONFIRMED"
        elif payload.action == "CLOSE":
            if row.rectify_status not in ("RECTIFIED", "ASSIGNED", "OPEN"):
                raise ServiceException("CONFLICT_STATE", 409)
            row.rectify_status = "VERIFIED"
            row.closed_at = datetime.now(timezone.utc).replace(tzinfo=None)
            self.audit.log_template("HazardTicket", 4, actor, row.id, ticket_id=row.id)
            self.db.commit()
            return build_hazard_ticket_dto(row)
        else:
            raise ServiceException("VALIDATION_FAILED", 422, detail="非法 action")
        self.audit.log_template(
            "HazardTicket", 2, actor, row.id, ticket_id=row.id, rectify_status=row.rectify_status,
        )
        self.db.commit()
        return build_hazard_ticket_dto(row)
