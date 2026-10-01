from src.constants.log_templates import LOG_TEMPLATES
from src.repositories.audit_log_repository import AuditLogRepository
from src.utils.formatters import audit_target


class AuditService:
    """所有写操作经此落日志；模板改动只在 constants/log_templates.py。"""

    def __init__(self, db):
        self.repo = AuditLogRepository(db)

    def log_template(self, entity, index, actor, target_id=None, **params):
        templates = LOG_TEMPLATES[entity]
        text = templates[index].format(actor=actor, **params)
        return self.repo.add(
            actor=actor,
            action=text.split(" ")[0],
            target_type=entity,
            target_id=target_id,
            detail=text,
        )

    def log(self, actor, entity, action, target_id=None, detail=None):
        return self.repo.add(
            actor=actor,
            action=action,
            target_type=entity,
            target_id=target_id,
            detail=detail or audit_target(entity, target_id),
        )

    def list(self, limit=100):
        return self.repo.find_all(limit=limit)
