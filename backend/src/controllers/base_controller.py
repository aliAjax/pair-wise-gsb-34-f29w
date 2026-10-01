from fastapi import HTTPException

from src.utils.exceptions import ServiceException


def call(service_method, *args, **kwargs):
    """controller 统一二次包装：service 抛 ServiceException，controller 转 HTTPException。"""
    try:
        return service_method(*args, **kwargs)
    except ServiceException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"code": exc.code, "message": exc.message},
        )
