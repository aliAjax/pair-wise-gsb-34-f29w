from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.settings import DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    if DATABASE_URL in ("sqlite://", "sqlite:///:memory:"):
        # 内存库需要 StaticPool 才能在多个连接间共享同一份数据
        engine = create_engine(
            DATABASE_URL,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            future=True,
            connect_args={"check_same_thread": False},
        )
else:
    engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
