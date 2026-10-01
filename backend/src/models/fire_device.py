from sqlalchemy import Column, DateTime, Integer, String

from src.config.database import Base


class FireDevice(Base):
    __tablename__ = "fire_device"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(Integer, nullable=False, index=True)
    device_code = Column(String(64), nullable=False, unique=True)
    device_type = Column(String(32), nullable=False)
    floor = Column(String(16), nullable=False)
    location_desc = Column(String(128), nullable=False)
    install_date = Column(DateTime, nullable=True)
    # NORMAL / OUTAGE / PENDING_REUSE / FAULT
    status = Column(String(32), nullable=False, default="NORMAL", index=True)
    next_maintenance_at = Column(DateTime, nullable=True)
    # 复役手续，逗号分隔的 REUSE_PAPERWORK_ITEMS 子集；停用期间清空，复役前需补齐
    reuse_paperwork = Column(String(128), nullable=False, default="")
