"""建筑楼栋 DTO。"""
from pydantic import BaseModel


class BuildingCreatePayload(BaseModel):
    name: str
    campus: str = ""
    floor_count: int = 1
    fire_grade: str = "SECOND"
    manager_id: int | None = None
    address_code: str = ""
