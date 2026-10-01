"""FastAPI 应用入口。

- 启动时 create_all（本地/演示；生产建议改用迁移目录）。
- 认证 -> RBAC -> 审计 三层中间件。
- 全局异常处理集中渲染错误码。
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src import models  # noqa: F401  确保所有模型已注册
from src.database import Base, engine, SessionLocal
from src.middlewares.audit_log_middleware import audit_log_middleware
from src.middlewares.auth_middleware import auth_middleware
from src.middlewares.error_handler_middleware import register_error_handlers
from src.middlewares.rbac_middleware import rbac_middleware
from src.routes.building_routes import router as building_router
from src.routes.fire_device_routes import router as fire_device_router
from src.routes.hazard_ticket_routes import router as hazard_ticket_router
from src.routes.inspection_result_routes import router as inspection_result_router
from src.routes.inspection_task_routes import router as inspection_task_router
from src.routes.outage_window_routes import router as outage_window_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动建表并注入幂等种子数据（本地/演示；生产建议改用迁移目录）。
    Base.metadata.create_all(bind=engine)
    from src.seed_runner import seed_if_empty

    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(title="消防设施巡检维保平台 fire-inspect", lifespan=lifespan)

# 注册顺序：后添加的先执行。想要 auth -> rbac -> audit 的调用顺序，
# 需按 audit、rbac、auth 的顺序添加。
app.middleware("http")(audit_log_middleware)
app.middleware("http")(rbac_middleware)
app.middleware("http")(auth_middleware)
register_error_handlers(app)


@app.get("/health")
def health():
    return {"status": "ok", "service": "fire-inspect"}


for _router in (
    building_router,
    fire_device_router,
    inspection_task_router,
    inspection_result_router,
    hazard_ticket_router,
    outage_window_router,
):
    app.include_router(_router)
