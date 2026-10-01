"""建筑楼栋控制器。"""
from fastapi import Depends, Request

from src.database import get_db
from src.services.building_service import BuildingService
from src.types.building_payload import BuildingCreatePayload


def _actor(request: Request) -> str:
    return str((getattr(request.state, "user", None) or {}).get("id", "system"))


def list_building(request: Request, db=Depends(get_db)):
    return BuildingService(db).list()


def create_building(payload: BuildingCreatePayload, request: Request,
                    db=Depends(get_db)):
    return BuildingService(db).create(payload, actor=_actor(request))
