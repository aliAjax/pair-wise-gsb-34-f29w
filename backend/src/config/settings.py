import os

PORT = int(os.getenv("PORT", "8000"))

# 部署环境走 PostgreSQL；本地无数据库时可用 DATABASE_URL=sqlite:///./fire_inspect.db
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "app_db")
DB_USER = os.getenv("DB_USER", "app_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "app_password")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

JWT_SECRET = os.getenv("JWT_SECRET", "local-dev-secret")
JWT_ALGORITHM = "HS256"

# 简单的本地演示账号：id / 角色 / 姓名
LOCAL_USERS = {
    1: {"id": 1, "name": "周巡检", "role": "INSPECTOR"},
    2: {"id": 2, "name": "吴维保", "role": "MAINTAINER"},
    3: {"id": 3, "name": "郑主管", "role": "SUPERVISOR"},
    4: {"id": 4, "name": "王审计", "role": "AUDITOR"},
}

ROLE_LABELS = {
    "INSPECTOR": "巡检员",
    "MAINTAINER": "维保商",
    "SUPERVISOR": "物业主管",
    "AUDITOR": "审计员",
}

# 接口限流：每窗口最大请求数
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 300
