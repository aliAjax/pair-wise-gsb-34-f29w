"""建筑楼栋路由。"""
from fastapi import APIRouter

from src.controllers.building_controller import create_building, list_building

router = APIRouter(prefix="/api/building", tags=["Building"])
router.get("")(list_building)
router.post("")(create_building)
