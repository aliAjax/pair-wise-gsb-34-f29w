from src.constants.error_codes import ERROR_CODES
from src.constants.error_messages import ERROR_MESSAGES


class ServiceException(Exception):
    """service 层异常：controller 必须再包装，不许只在全局中间件吞掉。"""

    def __init__(self, code: str, status_code: int = 400, **params):
        self.code = code if code in ERROR_CODES else ERROR_CODES["VALIDATION_FAILED"]
        self.status_code = status_code
        self.params = params
        template = ERROR_MESSAGES.get(self.code, code)
        try:
            self.message = template.format(**params)
        except KeyError:
            self.message = template
        super().__init__(self.message)
