"""规则 4：写入失败后恢复，重开续未生效设备，已占名额不重复也不丢失。"""
from datetime import datetime

import pytest

from src.models.capacity_holding import CapacityHolding
from src.models.device_outage_window import DeviceOutageWindow
from src.models.fire_device import FireDevice
from src.models.task_device_assignment import TaskDeviceAssignment
from src.services.outage_window_service import OutageWindowService
from src.types.outage_payload import OutageWindowCreatePayload
from src.utils.exceptions import ServiceError

START = datetime(2026, 10, 10, 8, 0, 0)
END = datetime(2026, 10, 10, 18, 0, 0)


def _draft(db, capacity=2):
    if capacity != 2:
        for device_id in (2, 3):
            db.get(FireDevice, device_id).capacity = capacity
        db.commit()
    svc = OutageWindowService(db)
    draft = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END,
    ))
    return svc, draft["id"]


def test_failure_mid_hold_then_resume_is_idempotent(db):
    svc, window_id = _draft(db)

    # 在容量阶段（逐条提交的中途）注入失败
    with pytest.raises(ServiceError) as exc:
        svc.confirm(window_id, force_fail_stage="HOLD_CAPACITY")
    assert "resume_key=" in str(exc.value)

    window = db.get(DeviceOutageWindow, window_id)
    assert window.write_stage == "HOLD_CAPACITY"
    assert window.last_error is not None

    # 第一条排期名额已落库（不丢失）
    pre_holdings = db.query(CapacityHolding).filter(
        CapacityHolding.window_id == window_id
    ).all()
    assert len(pre_holdings) == 1

    # 错误的 resume_key 必须被拒绝
    with pytest.raises(ServiceError) as bad:
        svc.resume(window_id, resume_key="wrong-key")
    assert bad.value.code == "OUTAGE_RESUME_KEY_MISMATCH"

    # 用正确的 key 恢复
    result = svc.resume(window_id, resume_key=window.resume_key)
    assert result["write_stage"] == "COMPLETED"
    assert result["outage_status"] == "CONFIRMED"

    holdings = db.query(CapacityHolding).filter(
        CapacityHolding.window_id == window_id
    ).all()
    # 两个排期各占 1 条，恢复不产生重复名额
    assert len(holdings) == 2
    assert {h.assignment_id for h in holdings} == {1, 2}

    # 备用 / 待补检关系各就各位
    derived = db.query(TaskDeviceAssignment).filter(
        TaskDeviceAssignment.window_id == window_id
    ).all()
    assert sorted(a.assignment_status for a in derived) == ["BACKUP", "BACKUP"]

    # 设备已真正停用
    assert db.get(FireDevice, 1).status == "OUT_OF_SERVICE"


def test_failure_at_device_mark_then_resume_completes(db):
    svc, window_id = _draft(db)
    with pytest.raises(ServiceError):
        svc.confirm(window_id, force_fail_stage="MARK_DEVICE_OUTAGE")
    window = db.get(DeviceOutageWindow, window_id)
    assert window.write_stage == "MARK_DEVICE_OUTAGE"
    # 容量分配已全部完成
    assert db.query(CapacityHolding).filter(
        CapacityHolding.window_id == window_id
    ).count() == 2
    # 设备尚未停用（未生效）
    assert db.get(FireDevice, 1).status == "NORMAL"

    result = svc.resume(window_id, resume_key=window.resume_key)
    assert result["write_stage"] == "COMPLETED"
    assert db.get(FireDevice, 1).status == "OUT_OF_SERVICE"
    # 名额数量不变
    assert db.query(CapacityHolding).filter(
        CapacityHolding.window_id == window_id
    ).count() == 2


def test_resume_then_replay_keeps_single_set_of_holdings(db):
    svc, window_id = _draft(db)
    svc.confirm(window_id)
    # 完成后再反复“恢复”，仍是同一批名额
    svc.resume(window_id, resume_key=db.get(DeviceOutageWindow, window_id).resume_key)
    svc.resume(window_id, resume_key=db.get(DeviceOutageWindow, window_id).resume_key)
    assert db.query(CapacityHolding).filter(
        CapacityHolding.window_id == window_id
    ).count() == 2
