"""RBAC：按角色限制写操作。停用确认 / 复役需要物业主管或维保商。"""
from fastapi.responses import JSONResponse

from src.constants.error_messages import ERROR_MESSAGES

# 角色 -> 允许的动作前缀
ROLE_PERMISSIONS = {
    "INSPECTOR": {"inspection", "result"},
    "MAINTAINER": {"outage", "device", "procedure", "restore", "hazard"},
    "SUPERVISOR": {"inspection", "result", "outage", "device", "procedure",
                   "restore", "hazard", "building"},
    "AUDITOR": set(),  # 只读
    "ADMIN": {"inspection", "result", "outage", "device", "procedure",
              "restore", "hazard", "building"},
}


def _action_for(path: str, method: str) -> str:
    if method == "GET":
        return "read"
    if "/outage-window" in path:
        if "/restore" in path:
            return "restore"
        if "/procedure" in path:
            return "procedure"
        return "outage"
    if "/fire-device" in path:
        return "device"
    if "/inspection" in path:
        return "inspection" if "task" in path else "result"
    if "/hazard-ticket" in path:
        return "hazard"
    if "/building" in path:
        return "building"
    return "other"


def allow_roles(role: str, action: str) -> bool:
    if action in ("read", "other"):
        return True
    return action in ROLE_PERMISSIONS.get(role, set())


async def rbac_middleware(request, call_next):
    user = getattr(request.state, "user", None) or {"role": "ADMIN"}
    action = _action_for(request.url.path, request.method)
    if not allow_roles(user.get("role", "ADMIN"), action):
        return JSONResponse(
            status_code=403,
            content={
                "code": "RBAC_DENIED",
                "message": ERROR_MESSAGES["RBAC_DENIED"].format(required=action),
            },
        )
    return await call_next(request)
