"""停用时段控制器：service 异常在这里二次包装为 HTTP 响应。"""
from fastapi import Depends, Request

from src.database import get_db
from src.services.outage_window_service import OutageWindowService
from src.types.outage_payload import (
    OutageChangePayload,
    OutageDraftSavePayload,
    OutageProcedurePayload,
    OutageWindowCreatePayload,
)
from src.utils.exceptions import BusinessException, ControllerError


def _service(db) -> OutageWindowService:
    return OutageWindowService(db)


def _actor(request: Request) -> str:
    user = getattr(request.state, "user", None) or {}
    return str(user.get("id", "system"))


def list_windows(request: Request, db=Depends(get_db)):
    try:
        return _service(db).list_windows()
    except BusinessException:
        raise
    except Exception as exc:  # controller 层兜底包装
        raise ControllerError("INTERNAL_ERROR", 500) from exc


def submit_window(payload: OutageWindowCreatePayload, request: Request,
                  db=Depends(get_db)):
    try:
        return _service(db).submit_draft(payload, actor=_actor(request))
    except BusinessException:
        raise


def get_window(window_id: int, request: Request, db=Depends(get_db)):
    return _service(db).get_window_dto(window_id)


def save_draft(payload: OutageDraftSavePayload, request: Request,
               db=Depends(get_db)):
    return _service(db).save_draft_content(payload, actor=_actor(request))


def list_drafts(window_id: int, request: Request, db=Depends(get_db)):
    return _service(db).list_drafts(window_id)


def confirm_window(window_id: int, request: Request, db=Depends(get_db)):
    return _service(db).confirm(window_id, actor=_actor(request))


def conflict_guard_confirm(window_id: int, request: Request,
                           owner_id: int, db=Depends(get_db)):
    """两个负责人同时确认重叠时段：后到者看到占用数量并保留草稿。"""
    return _service(db).confirm_with_conflict_guard(
        window_id, owner_id=owner_id, actor=_actor(request)
    )


def resume_window(window_id: int, request: Request, resume_key: str,
                  db=Depends(get_db)):
    return _service(db).resume(window_id, resume_key=resume_key,
                               actor=_actor(request))


def change_window(window_id: int, payload: OutageChangePayload, request: Request,
                  db=Depends(get_db)):
    return _service(db).change_window(window_id, payload, actor=_actor(request))


def list_holdings(window_id: int, request: Request, db=Depends(get_db)):
    return _service(db).list_holdings(window_id)


def list_window_assignments(window_id: int, request: Request, db=Depends(get_db)):
    return _service(db).list_assignments(window_id)


def register_procedure(window_id: int, payload: OutageProcedurePayload,
                       request: Request, db=Depends(get_db)):
    return _service(db).register_procedure(window_id, payload,
                                           actor=_actor(request))


def list_procedures(window_id: int, request: Request, db=Depends(get_db)):
    return _service(db).list_procedures(window_id)


def restore_device(device_id: int, request: Request, db=Depends(get_db)):
    return _service(db).restore_device(device_id, actor=_actor(request))
