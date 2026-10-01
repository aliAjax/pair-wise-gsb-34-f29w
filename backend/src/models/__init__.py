"""集中导出全部 ORM 模型，供 create_all 与仓储层引用。"""
from src.models.audit_log import AuditLog
from src.models.building import Building
from src.models.capacity_holding import CapacityHolding
from src.models.device_outage_window import DeviceOutageWindow
from src.models.fire_device import FireDevice
from src.models.hazard_ticket import HazardTicket
from src.models.inspection_result import InspectionResult
from src.models.inspection_task import InspectionTask
from src.models.outage_draft import OutageDraft
from src.models.outage_procedure import OutageProcedure
from src.models.task_device_assignment import TaskDeviceAssignment

__all__ = [
    "AuditLog",
    "Building",
    "CapacityHolding",
    "DeviceOutageWindow",
    "FireDevice",
    "HazardTicket",
    "InspectionResult",
    "InspectionTask",
    "OutageDraft",
    "OutageProcedure",
    "TaskDeviceAssignment",
]
