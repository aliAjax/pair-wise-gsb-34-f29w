"""巡检结果路由。"""
from fastapi import APIRouter

from src.controllers.inspection_result_controller import (
    create_inspection_result,
    list_inspection_result,
    review_inspection_result,
)

router = APIRouter(prefix="/api/inspection-result", tags=["InspectionResult"])
router.get("")(list_inspection_result)
router.post("")(create_inspection_result)
router.post("/{result_id}/review")(review_inspection_result)
