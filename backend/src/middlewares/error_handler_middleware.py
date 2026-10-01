from fastapi.responses import JSONResponse

from src.constants.error_messages import ERROR_MESSAGES
from src.utils.exceptions import ServiceException


async def error_handler_middleware(request, call_next):
    """全局兜底：只处理未被 controller 包装的异常；业务异常应在 controller 先包一层。"""
    try:
        return await call_next(request)
    except ServiceException as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": exc.message},
        )
    except Exception as exc:  # pragma: no cover - 兜底
        return JSONResponse(
            status_code=500,
            content={
                "code": "WRITE_FAILED",
                "message": ERROR_MESSAGES["WRITE_FAILED"].format(detail=str(exc)),
            },
        )
