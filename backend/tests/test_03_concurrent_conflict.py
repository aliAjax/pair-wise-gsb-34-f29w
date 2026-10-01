"""规则 3：两个负责人同时确认重叠时段，后到者看到占用数量并保留草稿。"""
from datetime import datetime

from src.models.device_outage_window import DeviceOutageWindow
from src.models.fire_device import FireDevice
from src.services.outage_window_service import OutageWindowService
from src.types.outage_payload import OutageWindowCreatePayload

START = datetime(2026, 10, 10, 8, 0, 0)
END = datetime(2026, 10, 10, 18, 0, 0)


def test_later_manager_sees_occupied_and_keeps_draft(db):
    # 容量仅够承接 1 个巡检项，先到者占满，后到者只能保留草稿。
    db.get(FireDevice, 2).capacity = 1
    db.get(FireDevice, 3).capacity = 0
    db.commit()

    svc = OutageWindowService(db)

    # 负责人 A 提交并确认 device 1 的停用
    draft_a = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END,
    ))
    svc.confirm(draft_a["id"])

    # 负责人 B 再登记一台同类型设备并提交重叠停用
    db.add(FireDevice(id=10, building_id=1, device_code="FE-010",
                      device_type="EXTINGUISHER", floor="4",
                      location_desc="4F", status="NORMAL", capacity=0))
    # 给 device 10 挂一个重叠的原排期
    from src.models.inspection_task import InspectionTask
    from src.models.task_device_assignment import TaskDeviceAssignment

    db.add(InspectionTask(id=9, building_id=1, inspector_id=209,
                          plan_date=START, task_type="EXTINGUISHER",
                          status="PLANNED"))
    db.add(TaskDeviceAssignment(id=90, task_id=9, building_id=1,
                                device_type="EXTINGUISHER",
                                planned_device_id=10, actual_device_id=10,
                                assignment_status="ORIGINAL"))
    db.commit()

    draft_b = svc.submit_draft(OutageWindowCreatePayload(
        device_id=10, owner_id=101, start_at=START, end_at=END,
    ))

    response = svc.confirm_with_conflict_guard(draft_b["id"], owner_id=101)
    assert response["conflict"] is True
    assert response["occupied_capacity"] >= 1
    assert response["draft_saved"] is True
    # 后到者窗口仍是草稿，未确认
    window_b = db.get(DeviceOutageWindow, draft_b["id"])
    assert window_b.outage_status == "DRAFT"
    # 草稿确实保留
    drafts = svc.list_drafts(draft_b["id"])
    assert len(drafts) == 1
    assert drafts[0]["owner_id"] == 101
    assert drafts[0]["observed_occupied"] == response["occupied_capacity"]


def test_concurrent_confirm_serialized_with_row_lock(db):
    """重复确认同一窗口：第二次走幂等重放，名额不重复（等价行锁串行化结果）。"""
    svc = OutageWindowService(db)
    draft = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END,
    ))
    window_id = draft["id"]

    first = svc.confirm(window_id)
    second = svc.confirm(window_id)  # 模拟后到者在锁释放后进入临界区

    assert first["write_stage"] == "COMPLETED"
    assert second.get("idempotent_replayed") is True

    from src.models.capacity_holding import CapacityHolding

    holdings = db.query(CapacityHolding).filter(
        CapacityHolding.window_id == window_id
    ).all()
    # 只有 2 个原排期，绝不会因为重复确认而出现 4 条占用
    assert len(holdings) == 2

    # 行锁仓储在 PostgreSQL 方言下会发出 SELECT ... FOR UPDATE
    locked = svc.window_repo.lock_row(window_id)
    assert locked is not None and locked.outage_status == "CONFIRMED"
