from sqlalchemy import Column, DateTime, Integer, String

from src.config.database import Base


class InspectionResult(Base):
    __tablename__ = "inspection_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    item_code = Column(String(64), nullable=False)
    # NORMAL / ABNORMAL
    result_status = Column(String(32), nullable=False, default="NORMAL")
    measured_value = Column(String(128), nullable=True)
    photo_url = Column(String(256), nullable=True)
    note = Column(String(256), nullable=True)
    # 停用时段一变化，引用这些设备的巡检结果作废待复核
    review_flag = Column(String(32), nullable=False, default="ACTIVE", index=True)
    voided_at = Column(DateTime, nullable=True)
    voided_by_outage_id = Column(Integer, nullable=True)
