"""消防设备控制器。"""
from fastapi import Depends, Request

from src.database import get_db
from src.services.fire_device_service import FireDeviceService
from src.types.fire_device_payload import FireDeviceCreatePayload


def _actor(request: Request) -> str:
    return str((getattr(request.state, "user", None) or {}).get("id", "system"))


def list_fire_device(request: Request, db=Depends(get_db)):
    return FireDeviceService(db).list()


def create_fire_device(payload: FireDeviceCreatePayload, request: Request,
                       db=Depends(get_db)):
    return FireDeviceService(db).create(payload, actor=_actor(request))
