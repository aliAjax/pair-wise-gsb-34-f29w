"""全局异常处理：统一把 BusinessException / 校验异常渲染为错误码响应。"""
from fastapi import Request
from fastapi.responses import JSONResponse

from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES
from src.utils.exceptions import BusinessException


def to_error_payload(exc):
    code = getattr(exc, "code", "INTERNAL_ERROR")
    return {"code": code, "message": str(exc)}


def register_error_handlers(app):
    @app.exception_handler(BusinessException)
    async def _handle_business(request: Request, exc: BusinessException):
        return JSONResponse(
            status_code=exc.http_status,
            content={"code": exc.code, "message": str(exc), "details": exc.fmt},
        )

    @app.exception_handler(Exception)
    async def _handle_unknown(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "code": ERROR_CODES["INTERNAL_ERROR"],
                "message": ERROR_MESSAGES["INTERNAL_ERROR"],
            },
        )
