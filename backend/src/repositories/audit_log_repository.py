"""审计日志数据访问层。"""
from datetime import datetime

from sqlalchemy.orm import Session

from src.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def write(self, *, actor: str, action: str, target_type: str,
              target_id: str = "", detail: str = "") -> AuditLog:
        row = AuditLog(
            actor=actor,
            action=action,
            target_type=target_type,
            target_id=str(target_id),
            detail=detail,
            created_at=datetime.utcnow(),
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list(self, limit: int = 100) ->list[AuditLog]:
        return list(
            self.db.query(AuditLog)
            .order_by(AuditLog.id.desc())
            .limit(limit)
            .all()
        )
