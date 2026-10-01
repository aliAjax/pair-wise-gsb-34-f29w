import logging
import time

logger = logging.getLogger("fire_inspect.access")


async def request_logger_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    cost_ms = int((time.perf_counter() - start) * 1000)
    logger.info("%s %s -> %s %sms", request.method, request.url.path, response.status_code, cost_ms)
    response.headers["x-response-time-ms"] = str(cost_ms)
    return response
