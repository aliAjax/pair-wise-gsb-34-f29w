import os


class Settings:
    """全局配置：集中读取环境变量，docker-compose / .env 注入。"""

    APP_NAME = "fire-inspect"
    PORT = int(os.getenv("PORT", "8000"))

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "app_db")
    DB_USER = os.getenv("DB_USER", "app_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "app_password")

    # 测试与本地脚本可通过 DATABASE_URL 直接覆盖（sqlite）。
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )

    JWT_SECRET = os.getenv("JWT_SECRET", "local-dev-secret")
    JWT_ALGORITHM = "HS256"

    # 备用设备容量：排队转待补检时的额外保护阈值（0 表示不额外限制）。
    BACKUP_CAPACITY_BUFFER = int(os.getenv("BACKUP_CAPACITY_BUFFER", "0"))


settings = Settings()
