"""规则 1：负责人提交停用时段后，同段巡检改用备用设备。"""
from datetime import datetime, timedelta

from src.models.task_device_assignment import TaskDeviceAssignment
from src.services.outage_window_service import OutageWindowService
from src.types.outage_payload import OutageWindowCreatePayload

START = datetime(2026, 10, 10, 8, 0, 0)
END = datetime(2026, 10, 10, 18, 0, 0)


def _submit_and_confirm(db):
    svc = OutageWindowService(db)
    draft = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END, reason="年度保养",
    ))
    result = svc.confirm(draft["id"])
    return svc, draft, result


def test_outage_reroutes_overlapping_tasks_to_backup(db):
    svc, draft, result = _submit_and_confirm(db)
    assert result["outage_status"] == "CONFIRMED"
    assert result["write_stage"] == "COMPLETED"

    assignments = db.query(TaskDeviceAssignment).order_by(TaskDeviceAssignment.id).all()
    statuses = [(a.planned_device_id, a.actual_device_id, a.assignment_status)
                for a in assignments]
    # 原关系保留
    originals = [a for a in assignments if a.assignment_status == "ORIGINAL"]
    assert len(originals) == 2
    # 两个同段任务都切到备用设备（2 / 3），不使用停用设备 1
    backups = [a for a in assignments if a.assignment_status == "BACKUP"]
    assert len(backups) == 2
    assert {a.actual_device_id for a in backups} <= {2, 3}
    assert all(a.actual_device_id != 1 for a in backups)
    assert all(a.origin_assignment_id is not None for a in backups)


def test_backup_capacity_counted(db):
    svc, draft, result = _submit_and_confirm(db)
    holdings = svc.list_holdings(draft["id"])
    assert sum(h["seats"] for h in holdings) == 2


def test_device_marked_out_of_service(db):
    from src.models.fire_device import FireDevice

    _submit_and_confirm(db)
    device = db.get(FireDevice, 1)
    assert device.status == "OUT_OF_SERVICE"
