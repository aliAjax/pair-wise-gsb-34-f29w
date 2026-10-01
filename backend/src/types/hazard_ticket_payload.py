from pydantic import BaseModel, ConfigDict


class HazardTicketPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    result_id: int
    severity: str = "MEDIUM"
    owner_id: int | None = None
    deadline: str | None = None


class RectifyTicketPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    rectify_note: str


class ReviewTicketPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # REINSTATE 恢复有效；CONFIRM_VOID 确认作废；CLOSE 复验关闭
    action: str
    rectify_note: str | None = None
