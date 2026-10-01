"""停机保养 × 巡检排期冲突：五条业务规则的接口级测试（内存 SQLite，逐用例重建）。"""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from src.config.database import Base, engine  # noqa: E402
from src.main import app  # noqa: E402
from src.seed import seed_database  # noqa: E402


@pytest.fixture()
def client():
    # 内存库 + StaticPool：逐用例重建表并重新播种，互不污染
    Base.metadata.drop_all(bind=engine)
    seed_database()
    with TestClient(app) as test_client:
        yield test_client


MAINTAINER = {"x-user-id": "2"}
SUPERVISOR = {"x-user-id": "3"}
INSPECTOR = {"x-user-id": "1"}


@pytest.fixture(scope="module")
def window():
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    day = timedelta(days=1)
    fmt = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")  # noqa: E731
    return {
        "start": fmt(now + 2 * day),
        "end": fmt(now + 2 * day + timedelta(hours=8)),
        "overlap_start": fmt(now + 2 * day + timedelta(hours=1)),
        "overlap_end": fmt(now + 2 * day + timedelta(hours=6)),
        "next_start": fmt(now + 3 * day),
        "next_end": fmt(now + 3 * day + timedelta(hours=5)),
    }


def test_rbac_inspector_cannot_create_building(client):
    res = client.post("/api/building", json={"name": "x", "campus": "y"}, headers=INSPECTOR)
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "RBAC_DENIED"


def test_rule1_submit_outage_reroute_queue_and_void(client, window):
    body = {
        "note": "消防泵检修",
        "items": [
            {"device_code": "HYD-001", "start_at": window["start"], "end_at": window["end"], "reason": "管网检修"},
            {"device_code": "SMK-001", "start_at": window["start"], "end_at": window["end"], "reason": "探头更换"},
        ],
    }
    res = client.post("/api/device-outage", json=body, headers=MAINTAINER)
    assert res.status_code == 200
    batch = res.json()

    hyd = next(i for i in batch["items"] if i["status"] == "CONFIRMED" and i["reroute"]["rerouted"])
    smk = next(i for i in batch["items"] if i["device_id"] != hyd["device_id"])
    # HYD-001 的窗口内任务改派给备用 HYD-002
    assert len(hyd["reroute"]["rerouted"]) == 1
    # SMK-001 三台窗口内任务在 2 台备用 × 容量 1 下：2 改派 + 1 排队待补检
    assert len(smk["reroute"]["rerouted"]) + len(smk["reroute"]["queued"]) == 3
    assert len(smk["reroute"]["queued"]) == 1
    # 设备进入停用
    assert client.get(f"/api/fire-device/{hyd['device_id']}").json()["status"] == "OUTAGE"
    # 停用生效，引用结果/隐患单作废待复核
    assert client.get("/api/inspection-result?review_flag=VOID_PENDING_REVIEW").json()
    assert client.get("/api/hazard-ticket?rectify_status=VOID_PENDING_REVIEW").json()


def test_rule2_later_confirmer_sees_occupied_count_and_keeps_draft(client, window):
    body = {"items": [{"device_code": "HYD-001", "start_at": window["start"], "end_at": window["end"]}]}
    first = client.post("/api/device-outage", json=body, headers=MAINTAINER).json()
    outage_id = first["items"][0]["id"]
    device_id = first["items"][0]["device_id"]

    preview = client.get(
        "/api/device-outage/occupied",
        params={"device_id": device_id, "start_at": window["overlap_start"], "end_at": window["overlap_end"]},
    ).json()
    assert preview["occupied_count"] == 1
    assert outage_id in preview["occupied_outage_ids"]

    # 另一负责人后到，重叠确认 -> 保留草稿
    second = client.post(
        "/api/device-outage",
        json={"items": [{"device_code": "HYD-001", "start_at": window["overlap_start"], "end_at": window["overlap_end"]}]},
        headers=SUPERVISOR,
    ).json()
    draft = next(i for i in second["items"] if i["status"] == "DRAFT")
    assert draft["occupied_count"] == 1
    # 草稿不抢占名额，设备仍是停用
    assert client.get(f"/api/fire-device/{device_id}").json()["status"] == "OUTAGE"


def test_rule3_resume_pending_is_idempotent_no_duplicate_no_loss(client, window):
    body = {
        "items": [
            {"device_code": "HYD-001", "start_at": window["start"], "end_at": window["end"]},
            {"device_code": "SPR-001", "start_at": window["start"], "end_at": window["end"]},
        ],
        "fail_device_codes": ["SPR-001"],
    }
    batch = client.post("/api/device-outage", json=body, headers=MAINTAINER).json()
    batch_id = batch["id"]
    hyd_item = next(i for i in batch["items"] if i["status"] == "CONFIRMED")
    pending = next(i for i in batch["items"] if i["status"] == "PENDING")
    assert len(hyd_item["reroute"]["rerouted"]) == 1

    resumed = client.post(f"/api/device-outage/batch/{batch_id}/resume", headers=MAINTAINER).json()
    # 已确认项不重放：条目数量不变，HYD 改派名额不翻倍
    assert len(resumed["items"]) == len(batch["items"])
    hyd_after = next(i for i in resumed["items"] if i["id"] == hyd_item["id"])
    assert len(hyd_after["reroute"]["rerouted"]) == 1
    # 失败项已恢复且不丢失：SPR-001 无同类型备用 -> 排队待补检
    spr = next(i for i in resumed["items"] if i["id"] == pending["id"])
    assert spr["status"] == "CONFIRMED"
    assert len(spr["reroute"]["queued"]) == 1
    # 再次续传：没有可续项
    again = client.post(f"/api/device-outage/batch/{batch_id}/resume", headers=MAINTAINER)
    assert again.status_code == 409
    assert again.json()["detail"]["code"] == "OUTAGE_BATCH_NOT_RESUMABLE"


def test_rule4_change_window_supersedes_and_revoids(client, window):
    first = client.post(
        "/api/device-outage",
        json={"items": [{"device_code": "HYD-001", "start_at": window["start"], "end_at": window["end"]}]},
        headers=MAINTAINER,
    ).json()
    target = first["items"][0]

    changed = client.patch(
        f"/api/device-outage/{target['id']}/window",
        json={"start_at": window["next_start"], "end_at": window["next_end"], "reason": "改期"},
        headers=MAINTAINER,
    )
    assert changed.status_code == 200
    new_item = changed.json()
    assert new_item["version"] == target["version"] + 1
    old = client.get(f"/api/device-outage/{target['id']}").json()
    assert old["status"] == "SUPERSEDED"
    assert "cascade" in new_item


def test_rule5_reuse_paperwork_gate(client, window):
    first = client.post(
        "/api/device-outage",
        json={"items": [{"device_code": "HYD-001", "start_at": window["start"], "end_at": window["end"]}]},
        headers=MAINTAINER,
    ).json()
    device_id = first["items"][0]["device_id"]

    # 手续未齐：409，设备挂待复役
    denied = client.post(f"/api/fire-device/{device_id}/reactivate", headers=SUPERVISOR)
    assert denied.status_code == 409
    assert denied.json()["detail"]["code"] == "PAPERWORK_INCOMPLETE"
    assert client.get(f"/api/fire-device/{device_id}").json()["status"] == "PENDING_REUSE"

    # 补齐手续后复役成功
    client.post(
        f"/api/fire-device/{device_id}/paperwork",
        json={"paperwork_items": ["MAINTENANCE_REPORT", "SAFETY_CHECK", "MANAGER_SIGN_OFF"]},
        headers=MAINTAINER,
    )
    ok = client.post(f"/api/fire-device/{device_id}/reactivate", headers=SUPERVISOR)
    assert ok.status_code == 200
    assert ok.json()["status"] == "NORMAL"


def test_pending_makeup_tasks_queryable(client, window):
    client.post(
        "/api/device-outage",
        json={"items": [{"device_code": "SPR-001", "start_at": window["start"], "end_at": window["end"]}]},
        headers=MAINTAINER,
    )
    tasks = client.get("/api/inspection-task?status=PENDING_MAKEUP").json()
    assert len(tasks) >= 1
    summary = client.get("/api/dashboard/summary").json()
    assert summary["pending_makeup_task_ids"]
