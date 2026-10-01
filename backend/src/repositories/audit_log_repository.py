from datetime import datetime, timezone

from src.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db):
        self.db = db

    def add(self, actor, action, target_type, target_id=None, detail=None):
        row = AuditLog(
            actor=str(actor),
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            detail=detail,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        self.db.add(row)
        self.db.flush()
        return row

    def find_all(self, limit=100):
        return self.db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
