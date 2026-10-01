from src.controllers.building_controller import (
    create_building,
    list_building,
)
from src.controllers.dashboard_controller import dashboard_summary, list_audit_logs
from src.controllers.device_outage_controller import (
    cancel_outage,
    change_outage_window,
    get_batch,
    list_batches,
    list_outages,
    occupied_preview,
    resume_batch,
    review_draft,
    submit_outages,
)
from src.controllers.fire_device_controller import (
    add_paperwork,
    create_fire_device,
    get_fire_device,
    list_fire_device,
    reactivate_fire_device,
)
from src.controllers.hazard_ticket_controller import (
    create_hazard_ticket,
    dispatch_hazard_ticket,
    list_hazard_ticket,
    rectify_hazard_ticket,
    review_or_close_hazard_ticket,
)
from src.controllers.inspection_result_controller import (
    create_inspection_result,
    list_inspection_result,
    review_voided_result,
)
from src.controllers.inspection_task_controller import (
    change_inspection_task_status,
    create_inspection_task,
    get_inspection_task,
    list_inspection_task,
)

__all__ = [
    "list_building",
    "create_building",
    "list_fire_device",
    "get_fire_device",
    "create_fire_device",
    "add_paperwork",
    "reactivate_fire_device",
    "list_inspection_task",
    "get_inspection_task",
    "create_inspection_task",
    "change_inspection_task_status",
    "list_inspection_result",
    "create_inspection_result",
    "review_voided_result",
    "list_hazard_ticket",
    "create_hazard_ticket",
    "dispatch_hazard_ticket",
    "rectify_hazard_ticket",
    "review_or_close_hazard_ticket",
    "list_outages",
    "list_batches",
    "get_batch",
    "occupied_preview",
    "submit_outages",
    "resume_batch",
    "review_draft",
    "change_outage_window",
    "cancel_outage",
    "dashboard_summary",
    "list_audit_logs",
]
