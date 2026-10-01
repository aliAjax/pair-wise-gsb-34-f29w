"""巡检任务路由。"""
from fastapi import APIRouter

from src.controllers.inspection_task_controller import (
    create_inspection_task,
    list_assignments,
    list_inspection_task,
)

router = APIRouter(prefix="/api/inspection-task", tags=["InspectionTask"])
router.get("")(list_inspection_task)
router.post("")(create_inspection_task)
router.get("/assignments")(list_assignments)
