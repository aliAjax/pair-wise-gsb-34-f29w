from fastapi import Depends, Query
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.controllers.base_controller import call
from src.middlewares.rbac_middleware import require_roles
from src.services.device_outage_service import DeviceOutageService
from src.types.device_outage_payload import (
    OutageChangePayload,
    OutageReviewDraftPayload,
    OutageSubmitPayload,
)


def list_outages(
    device_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return DeviceOutageService(db).list_outages(device_id=device_id, status=status)


def list_batches(db: Session = Depends(get_db)):
    return DeviceOutageService(db).list_batches()


def get_batch(batch_id: int, db: Session = Depends(get_db)):
    return call(DeviceOutageService(db).get_batch, batch_id)


def get_outage(outage_id: int, db: Session = Depends(get_db)):
    return call(DeviceOutageService(db).get_outage, outage_id)


def occupied_preview(
    device_id: int,
    start_at: str = Query(...),
    end_at: str = Query(...),
    db: Session = Depends(get_db),
):
    return call(DeviceOutageService(db).occupied_preview, device_id, start_at, end_at)


def submit_outages(
    payload: OutageSubmitPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("MAINTAINER", "SUPERVISOR")),
):
    """负责人提交停用时段；fail_device_codes 模拟部分写入失败，待续传恢复。"""
    return call(DeviceOutageService(db).submit, payload, actor=user["id"])


def resume_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("MAINTAINER", "SUPERVISOR")),
):
    """重开续未生效设备：只恢复 PENDING，已占名额不重复也不丢失。"""
    return call(DeviceOutageService(db).resume_batch, batch_id, actor=user["id"])


def review_draft(
    outage_id: int,
    payload: OutageReviewDraftPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("MAINTAINER", "SUPERVISOR")),
):
    return call(DeviceOutageService(db).review_draft, outage_id, payload, actor=user["id"])


def change_outage_window(
    outage_id: int,
    payload: OutageChangePayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("MAINTAINER", "SUPERVISOR")),
):
    """停用时段变化 -> 旧版作废、结果/隐患单作废待复核、新窗口重算改派。"""
    return call(DeviceOutageService(db).change_window, outage_id, payload, actor=user["id"])


def cancel_outage(
    outage_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("MAINTAINER", "SUPERVISOR")),
):
    return call(DeviceOutageService(db).cancel_outage, outage_id, actor=user["id"])
