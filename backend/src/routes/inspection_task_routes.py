from fastapi import APIRouter

from src.controllers.inspection_task_controller import (
    change_inspection_task_status,
    create_inspection_task,
    get_inspection_task,
    list_inspection_task,
)

router = APIRouter(prefix="/api/inspection-task", tags=["InspectionTask"])
router.get("", response_model=None)(list_inspection_task)
router.get("/{task_id}", response_model=None)(get_inspection_task)
router.post("", response_model=None)(create_inspection_task)
router.patch("/{task_id}/status", response_model=None)(change_inspection_task_status)
