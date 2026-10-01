"""消防设备路由。"""
from fastapi import APIRouter

from src.controllers.fire_device_controller import (
    create_fire_device,
    list_fire_device,
)

router = APIRouter(prefix="/api/fire-device", tags=["FireDevice"])
router.get("")(list_fire_device)
router.post("")(create_fire_device)
