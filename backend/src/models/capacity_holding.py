"""停用期间的容量占用名额。

恢复（断点续跑）时按 (window_id, backup_device_id, assignment_id) 判重，
保证已占名额不重复、不丢失。
"""
from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint

from src.database import Base


class CapacityHolding(Base):
    __tablename__ = "capacity_holding"
    __table_args__ = (
        UniqueConstraint(
            "window_id",
            "assignment_id",
            name="uq_holding_window_assignment",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    window_id = Column(Integer, nullable=False, index=True)
    backup_device_id = Column(Integer, nullable=False, index=True)
    assignment_id = Column(Integer, nullable=False)
    seats = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=True)
