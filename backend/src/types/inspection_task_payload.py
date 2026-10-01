from pydantic import BaseModel, ConfigDict


class InspectionTaskPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    building_id: int
    inspector_id: int | None = None
    plan_date: str
    task_type: str
    checklist_version: str = "v1"


class TaskStatusPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str
