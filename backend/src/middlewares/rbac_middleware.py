from fastapi import Depends, HTTPException, Request

from src.constants.error_messages import ERROR_MESSAGES


def current_user(request: Request):
    return getattr(request.state, "user", {"id": None, "role": "ANONYMOUS"})


def require_roles(*roles):
    """RBAC 依赖：在 route/controller/service 多层触达，而不是全局放行。"""

    def checker(user=Depends(current_user)):
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "RBAC_DENIED",
                    "message": ERROR_MESSAGES["RBAC_DENIED"].format(
                        role=user.get("role"), action="该操作",
                    ),
                },
            )
        return user

    return checker
