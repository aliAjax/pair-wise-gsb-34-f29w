"""消防设备 ORM 模型。

capacity 表示该设备作为“同类型巡检备用设备”时可承接的巡检项名额。
status 取值见 constants/device_status.py。
"""
from sqlalchemy import Column, Date, DateTime, Integer, String

from src.database import Base


class FireDevice(Base):
    __tablename__ = "fire_device"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(Integer, nullable=False, index=True)
    device_code = Column(String(64), nullable=False, unique=True)
    device_type = Column(String(32), nullable=False, index=True)
    floor = Column(String(16), nullable=False, default="1")
    location_desc = Column(String(255), nullable=False, default="")
    install_date = Column(Date, nullable=True)
    status = Column(String(32), nullable=False, default="NORMAL", index=True)
    next_maintenance_at = Column(DateTime, nullable=True)
    capacity = Column(Integer, nullable=False, default=3)
