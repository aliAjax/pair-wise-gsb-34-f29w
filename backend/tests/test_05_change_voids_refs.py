"""规则 5：停用时段一变化，引用这些设备的巡检结果和隐患整改单作废待复核。"""
from datetime import datetime, timedelta

from src.models.device_outage_window import DeviceOutageWindow
from src.models.hazard_ticket import HazardTicket
from src.models.inspection_result import InspectionResult
from src.services.outage_window_service import OutageWindowService
from src.types.outage_payload import OutageChangePayload, OutageWindowCreatePayload

START = datetime(2026, 10, 10, 8, 0, 0)
END = datetime(2026, 10, 10, 18, 0, 0)


def test_change_voids_results_and_tickets_pending_review(db):
    svc = OutageWindowService(db)
    draft = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END,
    ))
    svc.confirm(draft["id"])

    # 停用时段调整
    outcome = svc.change_window(draft["id"], OutageChangePayload(
        start_at=START + timedelta(days=1),
        end_at=END + timedelta(days=1),
        reason="配件延期",
    ))
    new_id = outcome["new_window"]["id"]
    assert outcome["superseded_window_id"] == draft["id"]

    old = db.get(DeviceOutageWindow, draft["id"])
    new = db.get(DeviceOutageWindow, new_id)
    assert old.outage_status == "SUPERSEDED"
    assert new.outage_status == "DRAFT"
    assert new.window_group_id == old.window_group_id
    assert new.version == old.version + 1

    # 引用设备 1 的巡检结果全部作废待复核
    result = db.get(InspectionResult, 1)
    assert result.review_status == "VOID_PENDING"
    assert result.voided_by_window_id == new_id

    # 关联隐患整改单同步作废待复核
    ticket = db.get(HazardTicket, 1)
    assert ticket.review_status == "VOID_PENDING"
    assert ticket.voided_by_window_id == new_id


def test_review_reconfirmed_then_change_voids_again(db):
    svc = OutageWindowService(db)
    draft = svc.submit_draft(OutageWindowCreatePayload(
        device_id=1, owner_id=100, start_at=START, end_at=END,
    ))
    svc.confirm(draft["id"])
    svc.change_window(draft["id"], OutageChangePayload(
        start_at=START + timedelta(days=1), end_at=END + timedelta(days=1),
    ))
    # 复核通过
    from src.services.inspection_result_service import InspectionResultService

    InspectionResultService(db).review(1, "RECONFIRMED")
    assert db.get(InspectionResult, 1).review_status == "RECONFIRMED"

    # 再次变更：重新确认过的结果也必须再次作废
    new_window = db.query(DeviceOutageWindow).filter(
        DeviceOutageWindow.window_group_id == 1,
        DeviceOutageWindow.version == 2,
    ).one()
    svc.change_window(new_window.id, OutageChangePayload(
        start_at=START + timedelta(days=2), end_at=END + timedelta(days=2),
    ))
    assert db.get(InspectionResult, 1).review_status == "VOID_PENDING"
