"""本地种子数据：全部来自本地数据库，禁止第三方 API。

场景设计（1 栋楼、4 台同类型灭火器、2 个重叠巡检任务）：
- device 1 计划停用（容量 3 的备用机 device 2/3/4 可承接）。
- 可通过把备用机容量调小来演示“容量不足排队转待补检”。
"""
from datetime import datetime, timedelta

from src.models.building import Building
from src.models.fire_device import FireDevice
from src.models.inspection_result import InspectionResult
from src.models.inspection_task import InspectionTask
from src.models.hazard_ticket import HazardTicket
from src.models.task_device_assignment import TaskDeviceAssignment

BASE_TIME = datetime(2026, 10, 10, 9, 0, 0)


def seed_if_empty(db):
    if db.query(Building).count() > 0:
        return False

    building = Building(
        id=1, name="1 号厂房", campus="东区园区", floor_count=6,
        fire_grade="SECOND", manager_id=100, address_code="320100",
    )
    db.add(building)

    devices = [
        FireDevice(id=1, building_id=1, device_code="FE-001",
                   device_type="EXTINGUISHER", floor="1",
                   location_desc="1F 大厅东侧", status="NORMAL", capacity=3),
        FireDevice(id=2, building_id=1, device_code="FE-002",
                   device_type="EXTINGUISHER", floor="2",
                   location_desc="2F 楼梯口", status="NORMAL", capacity=2),
        FireDevice(id=3, building_id=1, device_code="FE-003",
                   device_type="EXTINGUISHER", floor="3",
                   location_desc="3F 走廊", status="NORMAL", capacity=2),
        FireDevice(id=4, building_id=1, device_code="HD-001",
                   device_type="HYDRANT", floor="1",
                   location_desc="1F 消火栓", status="NORMAL", capacity=1),
    ]
    db.add_all(devices)

    task1 = InspectionTask(
        id=1, building_id=1, inspector_id=201, plan_date=BASE_TIME,
        task_type="EXTINGUISHER", status="PLANNED", checklist_version="v2026.1",
    )
    task2 = InspectionTask(
        id=2, building_id=1, inspector_id=202,
        plan_date=BASE_TIME + timedelta(hours=2),
        task_type="EXTINGUISHER", status="PLANNED", checklist_version="v2026.1",
    )
    db.add_all([task1, task2])

    # 原任务关系（ORIGINAL 永不删除）
    db.add_all([
        TaskDeviceAssignment(id=1, task_id=1, building_id=1,
                             device_type="EXTINGUISHER", planned_device_id=1,
                             actual_device_id=1, assignment_status="ORIGINAL"),
        TaskDeviceAssignment(id=2, task_id=2, building_id=1,
                             device_type="EXTINGUISHER", planned_device_id=1,
                             actual_device_id=1, assignment_status="ORIGINAL"),
    ])

    result1 = InspectionResult(
        id=1, task_id=1, device_id=1, item_code="PRESSURE",
        result_status="ABNORMAL", measured_value="0.8MPa",
        note="压力略低", review_status="ACTIVE",
    )
    db.add(result1)
    db.flush()
    db.add(HazardTicket(
        id=1, result_id=1, severity="MEDIUM", owner_id=301,
        deadline=BASE_TIME + timedelta(days=7),
        rectify_status="OPEN", review_status="ACTIVE",
    ))

    db.commit()
    return True
