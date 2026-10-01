"""巡检任务数据访问层。"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.inspection_task import InspectionTask


class InspectionTaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> list[InspectionTask]:
        return list(self.db.execute(select(InspectionTask).order_by(InspectionTask.plan_date.asc())).scalars().all())

    def get(self, task_id: int) -> InspectionTask | None:
        return self.db.get(InspectionTask, task_id)

    def list_overlapping(self, start_at: datetime, end_at: datetime) -> list[InspectionTask]:
        """计划时间与给定区间有交集的任务。"""
        return list(
            self.db.execute(
                select(InspectionTask).where(
                    InspectionTask.plan_date >= start_at,
                    InspectionTask.plan_date <= end_at,
                )
            ).scalars().all()
        )

    def add(self, **fields) -> InspectionTask:
        row = InspectionTask(**fields)
        self.db.add(row)
        self.db.flush()
        return row
