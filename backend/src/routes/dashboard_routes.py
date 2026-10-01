from fastapi import APIRouter

from src.controllers.dashboard_controller import dashboard_summary, list_audit_logs

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
router.get("/summary", response_model=None)(dashboard_summary)
router.get("/audit-logs", response_model=None)(list_audit_logs)
