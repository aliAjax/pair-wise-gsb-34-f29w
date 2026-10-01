"""停用时段路由：覆盖提交、确认、并发冲突、恢复、变更、手续、复役全链路。"""
from fastapi import APIRouter

from src.controllers.outage_window_controller import (
    change_window,
    confirm_window,
    conflict_guard_confirm,
    get_window,
    list_holdings,
    list_procedures,
    list_window_assignments,
    list_windows,
    list_drafts,
    register_procedure,
    restore_device,
    resume_window,
    save_draft,
    submit_window,
)

router = APIRouter(prefix="/api/outage-window", tags=["DeviceOutageWindow"])

router.get("")(list_windows)
router.post("")(submit_window)
router.post("/draft")(save_draft)
router.get("/{window_id}")(get_window)
router.get("/{window_id}/drafts")(list_drafts)
router.post("/{window_id}/confirm")(confirm_window)
router.post("/{window_id}/confirm-guard")(conflict_guard_confirm)
router.post("/{window_id}/resume")(resume_window)
router.post("/{window_id}/change")(change_window)
router.get("/{window_id}/holdings")(list_holdings)
router.get("/{window_id}/assignments")(list_window_assignments)
router.post("/{window_id}/procedure")(register_procedure)
router.get("/{window_id}/procedures")(list_procedures)
router.post("/device/{device_id}/restore")(restore_device)
