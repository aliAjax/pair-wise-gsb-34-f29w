"""巡检任务 ORM 模型。"""
from sqlalchemy import Column, DateTime, Integer, String

from src.database import Base


class InspectionTask(Base):
    __tablename__ = "inspection_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(Integer, nullable=False, index=True)
    inspector_id = Column(Integer, nullable=True)
    plan_date = Column(DateTime, nullable=False, index=True)
    task_type = Column(String(32), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="PLANNED", index=True)
    checklist_version = Column(String(32), nullable=False, default="v1")
    finished_at = Column(DateTime, nullable=True)
