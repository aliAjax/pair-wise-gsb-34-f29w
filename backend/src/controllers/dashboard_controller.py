from fastapi import Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.services.audit_service import AuditService
from src.services.dashboard_service import DashboardService


def dashboard_summary(db: Session = Depends(get_db)):
    return DashboardService(db).summary()


def list_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    rows = AuditService(db).list(limit=limit)
    return [
        {
            "id": row.id,
            "actor": row.actor,
            "action": row.action,
            "target_type": row.target_type,
            "target_id": row.target_id,
            "detail": row.detail,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]
