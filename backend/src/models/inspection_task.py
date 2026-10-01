from sqlalchemy import Column, DateTime, Integer, String

from src.config.database import Base


class InspectionTask(Base):
    __tablename__ = "inspection_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(Integer, nullable=False, index=True)
    inspector_id = Column(Integer, nullable=True)
    plan_date = Column(DateTime, nullable=False, index=True)
    task_type = Column(String(32), nullable=False)
    # PLANNED / IN_PROGRESS / SUBMITTED / REVIEWED / OVERDUE / PENDING_MAKEUP
    status = Column(String(32), nullable=False, default="PLANNED", index=True)
    checklist_version = Column(String(16), nullable=False, default="v1")
    finished_at = Column(DateTime, nullable=True)
