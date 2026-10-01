"""规则 2：备用容量不足时排队转待补检，原任务关系保留。"""
from datetime import datetime

from src.models.fire_device import FireDevice
from src.models.task_device_assignment import TaskDeviceAssignment
from src.services.outage_window_service import OutageWindowService
from src.types.outage_payload import OutageWindowCreatePayload

START = datetime(2026, 10, 10, 8, 0, 0)
END = datetime(2026, 10, 10, 18, 0, 0)


def test_capacity_shortage_queues_pending_recheck(db):
    # 备用机总共只能承接 1 个巡检项 -> 2 个任务里 1 个待补检
    db.get(FireDevice, 2).capacity = 1
    db.get(FireDevice, 3).capacity = 0
    db.commit()

    svc = OutageWindowService(db)
    draft = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END,
    ))
    svc.confirm(draft["id"])

    assignments = db.query(TaskDeviceAssignment).order_by(TaskDeviceAssignment.id).all()
    backups = [a for a in assignments if a.assignment_status == "BACKUP"]
    pending = [a for a in assignments if a.assignment_status == "PENDING_RECHECK"]
    originals = [a for a in assignments if a.assignment_status == "ORIGINAL"]

    assert len(backups) == 1
    assert len(pending) == 1
    # 排队按顺序，原关系保留
    assert pending[0].queue_position == 1
    assert pending[0].actual_device_id is None
    assert len(originals) == 2
    assert all(a.origin_assignment_id in {1, 2} for a in backups + pending)


def test_zero_backup_capacity_all_pending(db):
    for device_id in (2, 3):
        db.get(FireDevice, device_id).status = "OUT_OF_SERVICE"
    db.commit()

    svc = OutageWindowService(db)
    draft = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END,
    ))
    svc.confirm(draft["id"])

    pending = db.query(TaskDeviceAssignment).filter(
        TaskDeviceAssignment.assignment_status == "PENDING_RECHECK"
    ).order_by(TaskDeviceAssignment.queue_position).all()
    assert [p.queue_position for p in pending] == [1, 2]
    assert [p.origin_assignment_id for p in pending] == [1, 2]
