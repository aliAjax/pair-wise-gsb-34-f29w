from pydantic import BaseModel, ConfigDict


class BuildingPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    campus: str
    floor_count: int = 1
    fire_grade: str = "二级"
    manager_id: int | None = None
    address_code: str | None = None
