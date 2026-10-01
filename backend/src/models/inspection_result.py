"""巡检结果 ORM 模型。

review_status 支持停用时段变更后的“作废待复核”链路，
取值见 constants/review_status.py。
"""
from sqlalchemy import Column, DateTime, Integer, String, Text

from src.database import Base


class InspectionResult(Base):
    __tablename__ = "inspection_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    item_code = Column(String(64), nullable=False)
    result_status = Column(String(32), nullable=False, default="NORMAL")
    measured_value = Column(String(64), nullable=False, default="")
    photo_url = Column(String(255), nullable=True)
    note = Column(Text, nullable=True)
    review_status = Column(String(32), nullable=False, default="ACTIVE", index=True)
    voided_by_window_id = Column(Integer, nullable=True, index=True)
    reviewed_at = Column(DateTime, nullable=True)
