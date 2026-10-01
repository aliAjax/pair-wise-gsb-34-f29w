"""请求审计中间件：写操作（POST/PUT/PATCH/DELETE）打印访问轨迹。

业务级操作日志由 AuditService 按 constants/log_templates.py 落库，
此中间件只负责 HTTP 层访问留痕。
"""
import logging

logger = logging.getLogger("fire_inspect.audit")


async def audit_log_middleware(request, call_next):
    response = await call_next(request)
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        user = getattr(request.state, "user", None) or {}
        logger.info(
            "audit %s %s actor=%s role=%s status=%s",
            request.method,
            request.url.path,
            user.get("id", "-"),
            user.get("role", "-"),
            response.status_code,
        )
    return response
