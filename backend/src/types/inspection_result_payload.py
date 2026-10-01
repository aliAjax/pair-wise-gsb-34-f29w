"""巡检结果 DTO。"""
from pydantic import BaseModel


class InspectionResultCreatePayload(BaseModel):
    task_id: int
    device_id: int
    item_code: str
    result_status: str = "NORMAL"
    measured_value: str = ""
    photo_url: str | None = None
    note: str | None = None
