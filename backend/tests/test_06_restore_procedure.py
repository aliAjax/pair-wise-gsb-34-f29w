"""规则 6：复役前手续没补齐的设备不能回到正常。"""
from datetime import datetime

import pytest

from src.models.fire_device import FireDevice
from src.models.task_device_assignment import TaskDeviceAssignment
from src.services.outage_window_service import OutageWindowService
from src.types.outage_payload import OutageWindowCreatePayload, OutageProcedurePayload
from src.utils.exceptions import ServiceError

START = datetime(2026, 10, 10, 8, 0, 0)
END = datetime(2026, 10, 10, 18, 0, 0)


def _confirmed_window(db, capacity=2):
    if capacity != 2:
        from src.models.fire_device import FireDevice as FD

        # capacity=1 表示总备用容量只够 1 项（第二台容量置 0）
        db.get(FD, 2).capacity = capacity
        db.get(FD, 3).capacity = 0
        db.commit()
    svc = OutageWindowService(db)
    draft = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END,
    ))
    svc.confirm(draft["id"])
    return svc, draft["id"]


def test_restore_blocked_without_procedures(db):
    svc, window_id = _confirmed_window(db)
    assert db.get(FireDevice, 1).status == "OUT_OF_SERVICE"
    with pytest.raises(ServiceError) as exc:
        svc.restore_device(1)
    assert exc.value.code == "RESTORE_PROCEDURE_INCOMPLETE"
    message = str(exc.value)
    # 三种必备手续都缺失
    assert "MAINTENANCE_REPORT" in message
    assert "ACCEPTANCE_CHECK" in message
    assert "SAFETY_SIGN_OFF" in message
    assert db.get(FireDevice, 1).status == "OUT_OF_SERVICE"


def test_restore_allowed_after_all_procedures(db):
    svc, window_id = _confirmed_window(db)
    for procedure in ("MAINTENANCE_REPORT", "ACCEPTANCE_CHECK", "SAFETY_SIGN_OFF"):
        svc.register_procedure(window_id, OutageProcedurePayload(
            procedure_type=procedure, doc_url=f"/docs/{procedure}.pdf",
        ))
    result = svc.restore_device(1)
    assert result["status"] == "NORMAL"
    assert db.get(FireDevice, 1).status == "NORMAL"


def test_restore_normal_device_rejected(db):
    # 未停用设备不允许复役
    svc = OutageWindowService(db)
    with pytest.raises(ServiceError) as exc:
        svc.restore_device(2)
    assert exc.value.code == "DEVICE_NOT_OUT_OF_SERVICE"


def test_partial_procedure_still_blocked(db):
    svc, window_id = _confirmed_window(db)
    svc.register_procedure(window_id, OutageProcedurePayload(
        procedure_type="MAINTENANCE_REPORT",
    ))
    with pytest.raises(ServiceError) as exc:
        svc.restore_device(1)
    assert exc.value.code == "RESTORE_PROCEDURE_INCOMPLETE"
    assert "ACCEPTANCE_CHECK" in str(exc.value)


def test_restore_reschedules_pending_recheck(db):
    # 容量不足 -> 1 个待补检；复役后应补排（RESCHEDULED）且原关系仍在
    svc, window_id = _confirmed_window(db, capacity=1)
    pending = db.query(TaskDeviceAssignment).filter(
        TaskDeviceAssignment.assignment_status == "PENDING_RECHECK",
        TaskDeviceAssignment.window_id == window_id,
    ).all()
    assert len(pending) == 1

    for procedure in ("MAINTENANCE_REPORT", "ACCEPTANCE_CHECK", "SAFETY_SIGN_OFF"):
        svc.register_procedure(window_id, OutageProcedurePayload(
            procedure_type=procedure,
        ))
    result = svc.restore_device(1)
    assert result["rescheduled"] == 1

    statuses = [
        a.assignment_status
        for a in db.query(TaskDeviceAssignment).all()
    ]
    assert "ORIGINAL" in statuses
    assert "PENDING_RECHECK" in statuses  # 待补检行保留
    assert "RESCHEDULED" in statuses
