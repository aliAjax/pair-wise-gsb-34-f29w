"""隐患整改单 ORM 模型。

停用时段变更会级联使关联整改单作废待复核。
"""
from sqlalchemy import Column, DateTime, Integer, String, Text

from src.database import Base


class HazardTicket(Base):
    __tablename__ = "hazard_ticket"

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, nullable=False, index=True)
    severity = Column(String(32), nullable=False, default="MEDIUM")
    owner_id = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=True)
    rectify_status = Column(String(32), nullable=False, default="OPEN", index=True)
    rectify_note = Column(Text, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    review_status = Column(String(32), nullable=False, default="ACTIVE", index=True)
    voided_by_window_id = Column(Integer, nullable=True, index=True)
    reviewed_at = Column(DateTime, nullable=True)
