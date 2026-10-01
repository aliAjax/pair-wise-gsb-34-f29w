"""业务异常：service / controller 分层包装，携带错误码与格式化参数。"""
from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES


class BusinessException(Exception):
    def __init__(self, code: str, http_status: int = 400, **fmt):
        self.code = code if code in ERROR_CODES else "INTERNAL_ERROR"
        self.http_status = http_status
        self.fmt = fmt
        template = ERROR_MESSAGES.get(self.code, ERROR_MESSAGES["INTERNAL_ERROR"])
        try:
            message = template.format(**fmt)
        except KeyError:
            message = template
        super().__init__(message)


class ServiceError(BusinessException):
    """service 层包装标记，controller 会再次包装为响应。"""


class ControllerError(BusinessException):
    pass
