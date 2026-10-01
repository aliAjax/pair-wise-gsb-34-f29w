from fastapi import APIRouter

from src.controllers.fire_device_controller import (
    add_paperwork,
    create_fire_device,
    get_fire_device,
    list_fire_device,
    reactivate_fire_device,
)

router = APIRouter(prefix="/api/fire-device", tags=["FireDevice"])
router.get("", response_model=None)(list_fire_device)
router.get("/{device_id}", response_model=None)(get_fire_device)
router.post("", response_model=None)(create_fire_device)
# 复役手续补齐
router.post("/{device_id}/paperwork", response_model=None)(add_paperwork)
# 复役：手续未齐不能回到正常
router.post("/{device_id}/reactivate", response_model=None)(reactivate_fire_device)
