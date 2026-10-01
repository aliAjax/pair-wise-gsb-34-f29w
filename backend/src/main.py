from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.middlewares.audit_log_middleware import audit_log_middleware
from src.middlewares.auth_middleware import auth_middleware
from src.middlewares.error_handler_middleware import error_handler_middleware
from src.middlewares.rate_limit_middleware import rate_limit_middleware
from src.middlewares.request_logger_middleware import request_logger_middleware
from src.routes import (
    building_router,
    dashboard_router,
    device_outage_router,
    fire_device_router,
    hazard_ticket_router,
    inspection_result_router,
    inspection_task_router,
)
from src.seed import seed_database


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # 建表 + 首次播种（已存在数据则跳过）
    seed_database()
    yield


app = FastAPI(title="消防设施巡检维保平台", version="1.0.0", lifespan=lifespan)

# CORS 仅用于本地 dev（vite 20103 / 21103），部署时走 nginx 同源 /api 代理
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册顺序：后加的在最外层。错误处理要最外层兜底
app.middleware("http")(audit_log_middleware)
app.middleware("http")(auth_middleware)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(request_logger_middleware)
app.middleware("http")(error_handler_middleware)


@app.get("/health")
def health():
    return {"status": "ok", "service": "fire-inspect"}


app.include_router(building_router)
app.include_router(fire_device_router)
app.include_router(inspection_task_router)
app.include_router(inspection_result_router)
app.include_router(hazard_ticket_router)
app.include_router(device_outage_router)
app.include_router(dashboard_router)
