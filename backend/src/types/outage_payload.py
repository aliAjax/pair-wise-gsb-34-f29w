"""停用时段相关请求 / 响应 DTO。"""
from datetime import datetime

from pydantic import BaseModel, field_validator


class OutageWindowCreatePayload(BaseModel):
    device_id: int
    owner_id: int
    start_at: datetime
    end_at: datetime
    reason: str = ""

    @field_validator("end_at")
    @classmethod
    def _check_range(cls, value: datetime, info):
        start = info.data.get("start_at")
        if start is not None and value <= start:
            raise ValueError("end_at must be greater than start_at")
        return value


class OutageDraftSavePayload(BaseModel):
    window_id: int
    owner_id: int
    lock_version: int = 1
    payload: str = "{}"


class OutageConfirmPayload(BaseModel):
    resume_key: str | None = None


class OutageChangePayload(BaseModel):
    """停用时段变更（调整）。"""
    start_at: datetime
    end_at: datetime
    reason: str = ""

    @field_validator("end_at")
    @classmethod
    def _check_range(cls, value: datetime, info):
        start = info.data.get("start_at")
        if start is not None and value <= start:
            raise ValueError("end_at must be greater than start_at")
        return value


class OutageProcedurePayload(BaseModel):
    procedure_type: str
    doc_url: str | None = None


class ReviewPayload(BaseModel):
    review_status: str  # RECONFIRMED / REJECTED
