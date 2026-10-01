"""停用草稿。

两个负责人同时确认重叠时段时，后到者先看到占用数量，
其提交内容以草稿形式保留（带乐观锁版本）。
"""
from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from src.database import Base


class OutageDraft(Base):
    __tablename__ = "outage_draft"
    __table_args__ = (
        UniqueConstraint("window_id", "owner_id", name="uq_draft_window_owner"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    window_id = Column(Integer, nullable=False, index=True)
    owner_id = Column(Integer, nullable=False)
    payload = Column(String(2000), nullable=False, default="{}")
    observed_occupied = Column(Integer, nullable=False, default=0)
    lock_version = Column(Integer, nullable=False, default=1)
    updated_at = Column(DateTime, nullable=True)
