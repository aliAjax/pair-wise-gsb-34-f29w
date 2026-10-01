from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.controllers.base_controller import call
from src.middlewares.rbac_middleware import require_roles
from src.services.building_service import BuildingService
from src.types.building_payload import BuildingPayload


def list_building(db: Session = Depends(get_db)):
    return BuildingService(db).list()


def create_building(
    payload: BuildingPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("SUPERVISOR", "AUDITOR")),
):
    service = BuildingService(db)
    return call(service.create, payload, actor=user["id"])
