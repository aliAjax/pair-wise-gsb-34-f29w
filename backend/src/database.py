"""SQLAlchemy 引擎与会话管理。

生产环境使用 PostgreSQL（docker-compose 注入 DB_HOST 等），
测试环境通过环境变量 DATABASE_URL=sqlite:// 覆盖。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config.settings import settings


def _build_engine(url: str):
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, future=True, connect_args=connect_args)


engine = _build_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
