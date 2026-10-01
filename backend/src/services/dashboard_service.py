from src.constants.outage_status import BACKUP_SLOT_CAPACITY
from src.models.task_reroute import TaskReroute
from src.repositories.device_outage_repository import DeviceOutageRepository
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.hazard_ticket_repository import HazardTicketRepository
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.task_reroute_repository import TaskRerouteRepository


class DashboardService:
    def __init__(self, db):
        self.db = db
        self.device_repo = FireDeviceRepository(db)
        self.task_repo = InspectionTaskRepository(db)
        self.result_repo = InspectionResultRepository(db)
        self.ticket_repo = HazardTicketRepository(db)
        self.outage_repo = DeviceOutageRepository(db)
        self.reroute_repo = TaskRerouteRepository(db)

    def summary(self):
        devices = self.device_repo.find_all()
        tasks = self.task_repo.find_all()
        tickets = self.ticket_repo.find_all()
        outages = self.outage_repo.find_all()

        device_status_distribution = {}
        for device in devices:
            device_status_distribution[device.status] = device_status_distribution.get(device.status, 0) + 1

        task_status_distribution = {}
        for task in tasks:
            task_status_distribution[task.status] = task_status_distribution.get(task.status, 0) + 1

        finished = [t for t in tasks if t.status in ("REVIEWED",)]
        completion_rate = round(len(finished) / len(tasks), 4) if tasks else 0

        overdue_tickets = [t for t in tickets if t.rectify_status in ("OPEN", "ASSIGNED", "RECTIFIED")]
        critical_tickets = [t for t in tickets if t.severity == "CRITICAL" and t.rectify_status != "VERIFIED"]
        void_pending = [
            t for t in tickets if t.rectify_status == "VOID_PENDING_REVIEW"
        ]

        queued_task_ids = sorted({
            r.task_id for r in self.db.query(TaskReroute).filter_by(relation="QUEUED").all()
        })

        return {
            "device_total": len(devices),
            "device_status_distribution": device_status_distribution,
            "task_total": len(tasks),
            "task_status_distribution": task_status_distribution,
            "inspection_completion_rate": completion_rate,
            "open_ticket_count": len(overdue_tickets),
            "critical_ticket_count": len(critical_tickets),
            "void_pending_ticket_count": len(void_pending),
            "pending_makeup_task_ids": queued_task_ids,
            "outage_confirmed_count": sum(1 for o in outages if o.status == "CONFIRMED"),
            "outage_draft_count": sum(1 for o in outages if o.status == "DRAFT"),
            "outage_pending_count": sum(1 for o in outages if o.status == "PENDING"),
            "backup_slot_capacity": BACKUP_SLOT_CAPACITY,
        }
