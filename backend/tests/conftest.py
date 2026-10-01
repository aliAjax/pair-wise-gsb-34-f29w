"""pytest 公共夹具：每个用例独立的 SQLite 内存库 + FastAPI TestClient。"""
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from src import models  # noqa: E402,F401
from src import database as db_module  # noqa: E402


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 所有会话共享同一内存连接
        future=True,
    )
    db_module.Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, future=True)
    yield factory
    engine.dispose()


@pytest.fixture()
def db(session_factory):
    from src.seed_runner import seed_if_empty

    session = session_factory()
    seed_if_empty(session)
    session.commit()
    yield session
    session.close()


@pytest.fixture()
def client(session_factory, monkeypatch):
    # 让应用所有会话都落到同一个测试引擎上。
    bound = session_factory.kw["bind"]
    monkeypatch.setattr(db_module, "engine", bound)
    monkeypatch.setattr(db_module, "SessionLocal", session_factory)

    # main.py 通过 `from src.database import engine, SessionLocal` 持有引用，
    # 必须同步替换，否则 startup 仍会建在另一个内存库上。
    from src import main as main_module

    monkeypatch.setattr(main_module, "engine", bound)
    monkeypatch.setattr(main_module, "SessionLocal", session_factory)

    from src.main import app

    def _override_get_db():
        s = session_factory()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[db_module.get_db] = _override_get_db

    from src.seed_runner import seed_if_empty

    s = session_factory()
    seed_if_empty(s)
    s.commit()
    s.close()

    # 不使用 with 触发真实 startup（避免它再建一次库）；手动构造即可。
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
