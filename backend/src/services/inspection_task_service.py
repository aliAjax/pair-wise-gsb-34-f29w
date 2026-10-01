"""巡检任务业务服务：创建任务时同步建立 ORIGINAL 排期关系。"""
from src.constructors.inspection_task_factory import create_inspection_task_dto
from src.repositories.fire_device_repository import FireDeviceRepository
from src.repositories.inspection_task_repository import InspectionTaskRepository
from src.repositories.task_device_assignment_repository import (
    TaskDeviceAssignmentRepository,
)
from src.services.audit_service import AuditService
from src.types.inspection_task_payload import InspectionTaskCreatePayload


class InspectionTaskService:
    def __init__(self, db):
        self.db = db
        self.repo = InspectionTaskRepository(db)
        self.device_repo = FireDeviceRepository(db)
        self.assignment_repo = TaskDeviceAssignmentRepository(db)
        self.audit = AuditService(db)

    def list(self):
        return [create_inspection_task_dto(row) for row in self.repo.find_all()]

    def list_assignments(self, task_id: int | None = None):
        from src.constructors.outage_factory import create_assignment_dto

        rows = (
            self.assignment_repo.list_by_task(task_id)
            if task_id is not None
            else self.assignment_repo.list_all()
        )
        return [create_assignment_dto(row) for row in rows]

    def create(self, payload: InspectionTaskCreatePayload, actor: str = "system"):
        data = payload.model_dump()
        device_ids = data.pop("device_ids", [])
        row = self.repo.add(
            building_id=data["building_id"],
            inspector_id=data.get("inspector_id"),
            plan_date=data["plan_date"],
            task_type=data["task_type"],
            status="PLANNED",
            checklist_version=data.get("checklist_version", "v1"),
        )
        # 原任务关系：任务与计划设备的绑定，停用重排时不删除。
        devices = self.device_repo.list_by_ids(device_ids)
        for device in devices:
            self.assignment_repo.add(
                task_id=row.id,
                building_id=row.building_id,
                device_type=row.task_type,
                planned_device_id=device.id,
                actual_device_id=device.id,
                assignment_status="ORIGINAL",
                seats=1,
            )
        self.audit.log(
            "InspectionTask", 0, actor=actor, target_id=row.id,
            task_id=row.id, building_id=row.building_id,
            plan_date=row.plan_date.isoformat(),
        )
        self.db.commit()
        return create_inspection_task_dto(row)
