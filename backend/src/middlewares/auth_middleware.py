"""认证中间件：本地/演示用 x-user-id + x-role 头，生产换 JWT。"""
from fastapi.responses import JSONResponse

from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES

# 与前端 RBAC 角色保持一致
VALID_ROLES = {"INSPECTOR", "MAINTAINER", "SUPERVISOR", "AUDITOR", "ADMIN"}

PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


def _deny(code: str, status: int = 401) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"code": code, "message": ERROR_MESSAGES[code]},
    )


async def auth_middleware(request, call_next):
    if request.url.path in PUBLIC_PATHS or request.method == "OPTIONS":
        request.state.user = {"id": 0, "role": "ADMIN"}
        return await call_next(request)

    user_id = request.headers.get("x-user-id")
    role = request.headers.get("x-role", "SUPERVISOR").upper()
    if user_id and role not in VALID_ROLES:
        return _deny(ERROR_CODES["AUTH_REQUIRED"], 401)
    request.state.user = {"id": int(user_id) if user_id else 1, "role": role}
    return await call_next(request)
