from fastapi import APIRouter

from src.controllers.building_controller import create_building, list_building

router = APIRouter(prefix="/api/building", tags=["Building"])
router.get("", response_model=None)(list_building)
router.post("", response_model=None)(create_building)
