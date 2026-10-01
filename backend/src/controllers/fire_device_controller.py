from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.controllers.base_controller import call
from src.middlewares.rbac_middleware import require_roles
from src.services.fire_device_service import FireDeviceService
from src.types.fire_device_payload import FireDevicePayload, ReusePaperworkPayload


def list_fire_device(
    building_id: int | None = None,
    status: str | None = None,
    device_type: str | None = None,
    db: Session = Depends(get_db),
):
    return FireDeviceService(db).list(building_id=building_id, status=status, device_type=device_type)


def get_fire_device(device_id: int, db: Session = Depends(get_db)):
    service = FireDeviceService(db)
    return call(service.get, device_id)


def create_fire_device(
    payload: FireDevicePayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("SUPERVISOR", "MAINTAINER")),
):
    return call(FireDeviceService(db).create, payload, actor=user["id"])


def add_paperwork(
    device_id: int,
    payload: ReusePaperworkPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("MAINTAINER", "SUPERVISOR")),
):
    return call(FireDeviceService(db).add_paperwork, device_id, payload, actor=user["id"])


def reactivate_fire_device(
    device_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("SUPERVISOR", "MAINTAINER")),
):
    """复役：手续没补齐的设备不能回到正常。"""
    return call(FireDeviceService(db).reactivate, device_id, actor=user["id"])
