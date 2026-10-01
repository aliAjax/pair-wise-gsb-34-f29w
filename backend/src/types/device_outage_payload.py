from pydantic import BaseModel, ConfigDict


class OutageItemPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    device_code: str
    start_at: str
    end_at: str
    reason: str | None = None


class OutageSubmitPayload(BaseModel):
    """负责人一次提交多台设备的停用时段。

    fail_device_codes：模拟这些设备在首次写入时失败（落 PENDING 条目），
    之后调用续传接口恢复，已确认的名额不重复也不丢失。
    """

    model_config = ConfigDict(extra="ignore")

    items: list[OutageItemPayload]
    note: str | None = None
    fail_device_codes: list[str] = []


class OutageChangePayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    start_at: str | None = None
    end_at: str | None = None
    reason: str | None = None


class OutageReviewDraftPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # CONFIRM 确认草稿（可能再次冲突）；CANCEL 放弃草稿
    action: str
