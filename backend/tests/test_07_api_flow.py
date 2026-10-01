"""HTTP API 端到端：提交 -> 确认 -> 排期 -> 变更 -> 手续 -> 复役。"""
from datetime import datetime

from fastapi.testclient import TestClient


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["service"] == "fire-inspect"


def test_full_outage_flow_over_http(client: TestClient):
    headers = {"x-user-id": "100", "x-role": "MAINTAINER"}

    # 初始数据
    devices = client.get("/api/fire-device").json()
    assert len(devices) == 4

    # 1) 提交停用时段（草稿）
    payload = {
        "device_id": 1,
        "owner_id": 100,
        "start_at": "2026-10-10T08:00:00",
        "end_at": "2026-10-10T18:00:00",
        "reason": "年度保养",
    }
    res = client.post("/api/outage-window", json=payload, headers=headers)
    assert res.status_code == 200, res.text
    window = res.json()
    wid = window["id"]
    assert window["outage_status"] == "DRAFT"

    # 2) 确认
    res = client.post(f"/api/outage-window/{wid}/confirm", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["write_stage"] == "COMPLETED"

    # 3) 排期：2 个原关系保留（任务排期接口）+ 2 个备用（窗口接口）
    all_assignments = client.get("/api/inspection-task/assignments").json()
    assert sum(1 for a in all_assignments if a["assignment_status"] == "ORIGINAL") == 2
    assignments = client.get(
        f"/api/outage-window/{wid}/assignments"
    ).json()
    assert sum(1 for a in assignments if a["assignment_status"] == "BACKUP") == 2

    # 4) 占用名额
    holdings = client.get(f"/api/outage-window/{wid}/holdings").json()
    assert len(holdings) == 2

    # 5) 无手续复役 -> 409
    res = client.post("/api/outage-window/device/1/restore", headers=headers)
    assert res.status_code == 409
    err = res.json()
    assert err["code"] == "RESTORE_PROCEDURE_INCOMPLETE"
    assert "SAFETY_SIGN_OFF" in err["message"]

    # 6) 补齐三种手续
    for ptype in ("MAINTENANCE_REPORT", "ACCEPTANCE_CHECK", "SAFETY_SIGN_OFF"):
        r = client.post(
            f"/api/outage-window/{wid}/procedure",
            json={"procedure_type": ptype, "doc_url": f"/d/{ptype}.pdf"},
            headers=headers,
        )
        assert r.status_code == 200, r.text

    # 7) 复役成功
    res = client.post("/api/outage-window/device/1/restore", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "NORMAL"


def test_change_window_voids_refs_over_http(client: TestClient):
    headers = {"x-user-id": "100", "x-role": "SUPERVISOR"}
    window = client.post("/api/outage-window", json={
        "device_id": 1, "owner_id": 100,
        "start_at": "2026-10-10T08:00:00",
        "end_at": "2026-10-10T18:00:00",
    }, headers=headers).json()
    client.post(f"/api/outage-window/{window['id']}/confirm", headers=headers)

    res = client.post(f"/api/outage-window/{window['id']}/change", json={
        "start_at": "2026-10-11T08:00:00",
        "end_at": "2026-10-11T18:00:00",
        "reason": "延期",
    }, headers=headers)
    assert res.status_code == 200, res.text
    voided = res.json()["voided"]
    assert 1 in voided["result_ids"]
    assert 1 in voided["ticket_ids"]

    results = client.get("/api/inspection-result").json()
    r1 = next(r for r in results if r["id"] == 1)
    assert r1["review_status"] == "VOID_PENDING"

    tickets = client.get("/api/hazard-ticket").json()
    t1 = next(t for t in tickets if t["id"] == 1)
    assert t1["review_status"] == "VOID_PENDING"

    # 复核通过
    r = client.post("/api/inspection-result/1/review",
                    json={"review_status": "RECONFIRMED"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["review_status"] == "RECONFIRMED"


def test_rbac_denies_auditor_write(client: TestClient):
    headers = {"x-user-id": "9", "x-role": "AUDITOR"}
    res = client.post("/api/outage-window", json={
        "device_id": 1, "owner_id": 100,
        "start_at": "2026-10-10T08:00:00",
        "end_at": "2026-10-10T18:00:00",
    }, headers=headers)
    assert res.status_code == 403
    assert res.json()["code"] == "RBAC_DENIED"


def test_invalid_range_rejected(client: TestClient):
    res = client.post("/api/outage-window", json={
        "device_id": 1, "owner_id": 100,
        "start_at": "2026-10-10T18:00:00",
        "end_at": "2026-10-10T08:00:00",
    }, headers={"x-role": "MAINTAINER"})
    assert res.status_code == 422


def test_conflict_guard_keeps_draft_when_full(client: TestClient):
    headers = {"x-role": "MAINTAINER"}
    # 容量只够 1 项
    devices = client.get("/api/fire-device").json()
    # 直接走 service 调整容量更直接
    from src.database import SessionLocal

    from src.models.fire_device import FireDevice

    db = SessionLocal()
    db.get(FireDevice, 2).capacity = 1
    db.get(FireDevice, 3).capacity = 0
    db.commit()
    db.close()

    w1 = client.post("/api/outage-window", json={
        "device_id": 1, "owner_id": 100,
        "start_at": "2026-10-10T08:00:00",
        "end_at": "2026-10-10T18:00:00",
    }, headers=headers).json()
    client.post(f"/api/outage-window/{w1['id']}/confirm", headers=headers)

    # 第二个负责人登记同类型新设备 + 重叠窗口
    db = SessionLocal()
    from src.models.fire_device import FireDevice as FD
    from src.models.inspection_task import InspectionTask
    from src.models.task_device_assignment import TaskDeviceAssignment

    db.add(FD(id=10, building_id=1, device_code="FE-010",
              device_type="EXTINGUISHER", floor="4", location_desc="4F",
              status="NORMAL", capacity=0))
    db.add(InspectionTask(id=9, building_id=1, inspector_id=209,
                          plan_date=datetime(2026, 10, 10, 9, 0),
                          task_type="EXTINGUISHER", status="PLANNED"))
    db.add(TaskDeviceAssignment(id=90, task_id=9, building_id=1,
                                device_type="EXTINGUISHER", planned_device_id=10,
                                actual_device_id=10, assignment_status="ORIGINAL"))
    db.commit()
    db.close()

    w2 = client.post("/api/outage-window", json={
        "device_id": 10, "owner_id": 101,
        "start_at": "2026-10-10T08:00:00",
        "end_at": "2026-10-10T18:00:00",
    }, headers=headers).json()
    res = client.post(
        f"/api/outage-window/{w2['id']}/confirm-guard?owner_id=101",
        headers=headers,
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["conflict"] is True
    assert body["draft_saved"] is True
    assert body["occupied_capacity"] >= 1
    drafts = client.get(f"/api/outage-window/{w2['id']}/drafts").json()
    assert len(drafts) == 1
