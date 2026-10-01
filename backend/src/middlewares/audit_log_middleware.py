import logging

logger = logging.getLogger("fire_inspect.audit")


async def audit_log_middleware(request, call_next):
    """访问层审计日志：写操作的业务审计由 AuditService 落 audit_log 表。"""
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        user = getattr(request.state, "user", {})
        logger.info("write %s %s by %s", request.method, request.url.path, user.get("id"))
    return await call_next(request)
