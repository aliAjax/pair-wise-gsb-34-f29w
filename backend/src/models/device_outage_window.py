"""设备停用时段。

- 负责人提交停用时段，DRAFT 为草稿，CONFIRMED 后设备真正停用。
- 时段发生调整时旧版本置 SUPERSEDED，新版本继承 window_group_id，
  并触发引用设备的巡检结果 / 整改单作废待复核。
- write_stage / resume_key 支撑“写入失败后恢复”的断点续跑。
"""
from sqlalchemy import Column, DateTime, Integer, String

from src.database import Base


class DeviceOutageWindow(Base):
    __tablename__ = "device_outage_window"

    id = Column(Integer, primary_key=True, autoincrement=True)
    window_group_id = Column(Integer, nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    device_id = Column(Integer, nullable=False, index=True)
    owner_id = Column(Integer, nullable=False)
    start_at = Column(DateTime, nullable=False, index=True)
    end_at = Column(DateTime, nullable=False, index=True)
    reason = Column(String(255), nullable=False, default="")
    outage_status = Column(String(32), nullable=False, default="DRAFT", index=True)

    # 已占用的同栋同类型备用容量（确认时统计并快照）。
    occupied_capacity = Column(Integer, nullable=False, default=0)
    demanded_capacity = Column(Integer, nullable=False, default=0)

    # 断点续跑：最近成功阶段 + 恢复键。
    write_stage = Column(String(64), nullable=False, default="PERSIST_WINDOW")
    resume_key = Column(String(64), nullable=True, index=True)
    last_error = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
