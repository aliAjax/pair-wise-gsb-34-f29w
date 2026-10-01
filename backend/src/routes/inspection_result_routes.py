from fastapi import APIRouter

from src.controllers.inspection_result_controller import (
    create_inspection_result,
    list_inspection_result,
    review_voided_result,
)

router = APIRouter(prefix="/api/inspection-result", tags=["InspectionResult"])
router.get("", response_model=None)(list_inspection_result)
router.post("", response_model=None)(create_inspection_result)
# 停用时段变化导致作废后的复核
router.post("/{result_id}/review", response_model=None)(review_voided_result)
