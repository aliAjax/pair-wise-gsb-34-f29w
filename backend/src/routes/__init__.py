from src.routes.building_routes import router as building_router
from src.routes.dashboard_routes import router as dashboard_router
from src.routes.device_outage_routes import router as device_outage_router
from src.routes.fire_device_routes import router as fire_device_router
from src.routes.hazard_ticket_routes import router as hazard_ticket_router
from src.routes.inspection_result_routes import router as inspection_result_router
from src.routes.inspection_task_routes import router as inspection_task_router

__all__ = [
    "building_router",
    "fire_device_router",
    "inspection_task_router",
    "inspection_result_router",
    "hazard_ticket_router",
    "device_outage_router",
    "dashboard_router",
]
