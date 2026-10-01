from sqlalchemy import Column, DateTime, Integer, String

from src.config.database import Base


class DeviceOutage(Base):
    """消防设备停用时段。同一批次同一设备改窗后会产生新版本行。"""

    __tablename__ = "device_outage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(Integer, nullable=True, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    reason = Column(String(256), nullable=True)
    # DRAFT / CONFIRMED / SUPERSEDED / CANCELLED / PENDING
    status = Column(String(32), nullable=False, default="DRAFT", index=True)
    version = Column(Integer, nullable=False, default=1)
    confirmed_by = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    # DRAFT 时回填当时的占用数量（后到者看到占用数量）
    occupied_count = Column(Integer, nullable=False, default=0)
    # 与本条冲突的已确认时段 id，逗号分隔
    conflict_outage_ids = Column(String(128), nullable=False, default="")
