"""消防设备 DTO。"""
from datetime import date, datetime

from pydantic import BaseModel


class FireDeviceCreatePayload(BaseModel):
    building_id: int
    device_code: str
    device_type: str
    floor: str = "1"
    location_desc: str = ""
    install_date: date | None = None
    next_maintenance_at: datetime | None = None
    capacity: int = 3
