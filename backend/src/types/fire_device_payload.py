from pydantic import BaseModel, ConfigDict


class FireDevicePayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    building_id: int
    device_code: str
    device_type: str
    floor: str
    location_desc: str
    install_date: str | None = None
    next_maintenance_at: str | None = None


class ReusePaperworkPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # 本次补齐的手续项，取值见 REUSE_PAPERWORK_ITEMS
    paperwork_items: list[str]
