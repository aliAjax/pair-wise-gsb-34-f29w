"""任务-设备排期仓储。"""
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.models.inspection_task import InspectionTask
from src.models.task_device_assignment import TaskDeviceAssignment


class TaskDeviceAssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, **fields) -> TaskDeviceAssignment:
        row = TaskDeviceAssignment(**fields)
        self.db.add(row)
        self.db.flush()
        return row

    def get(self, assignment_id: int) -> TaskDeviceAssignment | None:
        return self.db.get(TaskDeviceAssignment, assignment_id)

    def find_derived(self, origin_id: int, window_id: int) -> TaskDeviceAssignment | None:
        """同一停用时段下，原排期是否已经派生过备用 / 待补检行（幂等关键）。"""
        return self.db.execute(
            select(TaskDeviceAssignment).where(
                TaskDeviceAssignment.origin_assignment_id == origin_id,
                TaskDeviceAssignment.window_id == window_id,
            ).limit(1)
        ).scalar_one_or_none()

    def list_originals_for_window(
        self, *, building_id: int, device_type: str, device_ids: list[int],
        plan_start, plan_end,
    ) -> list[TaskDeviceAssignment]:
        """与停用时段重叠的原始排期：同栋、同类型、计划设备停用、任务计划时间相交。"""
        if not device_ids:
            return []
        return list(
            self.db.execute(
                select(TaskDeviceAssignment)
                .join(
                    InspectionTask,
                    InspectionTask.id == TaskDeviceAssignment.task_id,
                )
                .where(
                    TaskDeviceAssignment.assignment_status == "ORIGINAL",
                    TaskDeviceAssignment.building_id == building_id,
                    TaskDeviceAssignment.device_type == device_type,
                    TaskDeviceAssignment.planned_device_id.in_(device_ids),
                    InspectionTask.plan_date >= plan_start,
                    InspectionTask.plan_date <= plan_end,
                )
                .order_by(TaskDeviceAssignment.id.asc())
            ).scalars().all()
        )

    def max_queue_position(self, window_id: int) -> int:
        value = self.db.execute(
            select(func.coalesce(func.max(TaskDeviceAssignment.queue_position), 0)).where(
                TaskDeviceAssignment.window_id == window_id,
                TaskDeviceAssignment.assignment_status == "PENDING_RECHECK",
            )
        ).scalar_one()
        return int(value or 0)

    def list_pending(self, window_id: int | None = None) -> list[TaskDeviceAssignment]:
        stmt = select(TaskDeviceAssignment).where(
            TaskDeviceAssignment.assignment_status == "PENDING_RECHECK"
        )
        if window_id is not None:
            stmt = stmt.where(TaskDeviceAssignment.window_id == window_id)
        stmt = stmt.order_by(TaskDeviceAssignment.queue_position.asc())
        return list(self.db.execute(stmt).scalars().all())

    def list_all(self) -> list[TaskDeviceAssignment]:
        return list(
            self.db.execute(
                select(TaskDeviceAssignment).order_by(TaskDeviceAssignment.id.asc())
            ).scalars().all()
        )

    def list_by_task(self, task_id: int) -> list[TaskDeviceAssignment]:
        return list(
            self.db.execute(
                select(TaskDeviceAssignment).where(
                    TaskDeviceAssignment.task_id == task_id
                ).order_by(TaskDeviceAssignment.id.asc())
            ).scalars().all()
        )
