"""停用时段变化的级联处理：

- 引用这些设备的巡检结果 -> VOID_PENDING_REVIEW（作废待复核）
- 关联的隐患整改单 -> VOID_PENDING_REVIEW（已复验关闭的除外）
- 作废记录携带 outage_id，复核人可选择恢复或确认作废
"""

from datetime import datetime, timezone

from src.constants.log_templates import LOG_TEMPLATES
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_result_repository import InspectionResultRepository


class CascadeVoidService:
    def __init__(self, db, audit):
        self.db = db
        self.audit = audit
        self.result_repo = InspectionResultRepository(db)
        self.ticket_repo = HazardTicketRepository(db)

    def void_for_outage(self, outage, actor):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        results = self.result_repo.find_by_devices([outage.device_id], only_active=True)
        tickets = self.ticket_repo.find_by_devices([outage.device_id])

        result_ids = []
        for result in results:
            result.review_flag = "VOID_PENDING_REVIEW"
            result.voided_at = now
            result.voided_by_outage_id = outage.id
            result_ids.append(result.id)
            self.audit.log(
                actor, "InspectionResult", "InspectionResult.void", result.id,
                detail=LOG_TEMPLATES["InspectionResult"][3].format(result_id=result.id),
            )

        ticket_ids = []
        for ticket in tickets:
            ticket.rectify_status = "VOID_PENDING_REVIEW"
            ticket.voided_at = now
            ticket.voided_by_outage_id = outage.id
            ticket.closed_at = None
            ticket_ids.append(ticket.id)
            self.audit.log(
                actor, "HazardTicket", "HazardTicket.void", ticket.id,
                detail=LOG_TEMPLATES["HazardTicket"][3].format(ticket_id=ticket.id),
            )

        return {
            "voided_result_ids": result_ids,
            "voided_ticket_ids": ticket_ids,
            "voided_count": len(result_ids) + len(ticket_ids),
        }
