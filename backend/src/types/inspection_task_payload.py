"""巡检任务创建 DTO，同时携带任务对设备的初始排期。"""
from datetime import datetime

from pydantic import BaseModel


class InspectionTaskCreatePayload(BaseModel):
    building_id: int
    inspector_id: int | None = None
    plan_date: datetime
    task_type: str
    checklist_version: str = "v1"
    device_ids: list[int] = []
