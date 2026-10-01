import threading
import time
from collections import defaultdict, deque

from fastapi.responses import JSONResponse

from src.config.settings import RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

_BUCKETS = defaultdict(deque)
_LOCK = threading.Lock()


async def rate_limit_middleware(request, call_next):
    """简单固定窗口限流；超限返回 RATE_LIMITED，错误码在 constants/error_codes.py。"""
    if request.url.path != "/health":
        now = time.monotonic()
        client = request.client.host if request.client else "local"
        limited = False
        with _LOCK:
            bucket = _BUCKETS[client]
            while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
                bucket.popleft()
            if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
                limited = True
            else:
                bucket.append(now)
        if limited:
            return JSONResponse(
                status_code=429,
                content={"code": "RATE_LIMITED", "message": "请求过于频繁，请稍后再试"},
                headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )
    return await call_next(request)
