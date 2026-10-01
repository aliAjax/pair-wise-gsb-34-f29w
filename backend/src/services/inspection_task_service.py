from src.constructors.inspection_task_factory import build_inspection_task_dto
from src.repositories.inspection_result_repository import InspectionResultRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.services.audit_service import AuditService
from src.utils.exceptions import ServiceException
from src.utils.formatters import parse_dt


class InspectionTaskService:
    def __init__(self, db):
        self.db = db
        self.repo = InspectionTaskRepository(db)
        self.result_repo = InspectionResultRepository(db)
        self.audit = AuditService(db)

    def list(self, status=None, building_id=None):
        rows = self.repo.find_all(status=status, building_id=building_id)
        tasks = [build_inspection_task_dto(row) for row in rows]
        # 附带每个任务的检查项数量与作废数量，供“巡检任务”页展示改派/待补检上下文
        for task in tasks:
            results = self.result_repo.find_all(task_id=task["id"])
            task["result_count"] = len(results)
            task["voided_count"] = sum(1 for r in results if r.review_flag == "VOID_PENDING_REVIEW")
        return tasks

    def get(self, task_id):
        row = self.repo.get(task_id)
        if row is None:
            raise ServiceException("TASK_NOT_FOUND", 404, task_id=task_id)
        dto = build_inspection_task_dto(row)
        dto["results"] = [r.id for r in self.result_repo.find_all(task_id=task_id)]
        return dto

    def create(self, payload, actor):
        row = self.repo.create(
            building_id=payload.building_id,
            inspector_id=payload.inspector_id,
            plan_date=parse_dt(payload.plan_date),
            task_type=payload.task_type,
            status="PLANNED",
            checklist_version=payload.checklist_version,
        )
        self.audit.log_template(
            "InspectionTask", 0, actor, row.id,
            plan_date=row.plan_date.strftime("%Y-%m-%d %H:%M"), task_type=row.task_type,
        )
        self.db.commit()
        return self.get(row.id)

    def change_status(self, task_id, payload, actor):
        row = self.repo.get(task_id)
        if row is None:
            raise ServiceException("TASK_NOT_FOUND", 404, task_id=task_id)
        valid = {"PLANNED", "IN_PROGRESS", "SUBMITTED", "REVIEWED", "OVERDUE", "PENDING_MAKEUP"}
        if payload.status not in valid:
            raise ServiceException("VALIDATION_FAILED", 422, detail=f"非法任务状态 {payload.status}")
        previous = row.status
        row.status = payload.status
        self.audit.log_template(
            "InspectionTask", 2, actor, row.id,
            task_id=row.id, from_status=previous, to_status=payload.status,
        )
        self.db.commit()
        return self.get(task_id)
