from pydantic import BaseModel, ConfigDict


class InspectionResultPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    task_id: int
    device_id: int
    item_code: str
    result_status: str = "NORMAL"
    measured_value: str | None = None
    photo_url: str | None = None
    note: str | None = None


class ReviewResultPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # REINSTATE 恢复有效；CONFIRM_VOID 确认作废
    action: str
    note: str | None = None
