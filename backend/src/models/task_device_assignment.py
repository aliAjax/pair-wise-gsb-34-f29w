"""任务-设备排期关系。

原任务关系保留：ORIGINAL 行不删除；停用期间新增 BACKUP 行，
容量不足时新增 PENDING_RECHECK 行并携带 queue_position。
"""
from sqlalchemy import Column, Integer, String

from src.database import Base


class TaskDeviceAssignment(Base):
    __tablename__ = "task_device_assignment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)
    building_id = Column(Integer, nullable=False, index=True)
    device_type = Column(String(32), nullable=False, index=True)
    planned_device_id = Column(Integer, nullable=False)
    actual_device_id = Column(Integer, nullable=True)
    assignment_status = Column(String(32), nullable=False, default="ORIGINAL", index=True)
    window_id = Column(Integer, nullable=True, index=True)
    origin_assignment_id = Column(Integer, nullable=True, index=True)
    queue_position = Column(Integer, nullable=True)
    seats = Column(Integer, nullable=False, default=1)
