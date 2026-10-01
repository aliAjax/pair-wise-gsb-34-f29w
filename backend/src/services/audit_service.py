"""审计日志服务：按 constants/log_templates.py 模板渲染并落库。"""
from src.constants.log_templates import LOG_TEMPLATES
from src.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    def __init__(self, db):
        self.db = db
        self.repo = AuditLogRepository(db)

    def log(self, entity: str, index: int, *, actor: str = "system",
            target_type: str | None = None, target_id: str = "", **kwargs):
        templates = LOG_TEMPLATES.get(entity, [])
        action = templates[index] if 0 <= index < len(templates) else f"{entity}.unknown"
        try:
            detail = action.format(**kwargs)
        except KeyError:
            detail = action
        return self.repo.write(
            actor=actor,
            action=detail,
            target_type=target_type or entity,
            target_id=target_id,
            detail=detail,
        )
