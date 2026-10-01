from sqlalchemy import Column, DateTime, Integer, String

from src.config.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor = Column(String(64), nullable=False)
    action = Column(String(128), nullable=False)
    target_type = Column(String(64), nullable=False)
    target_id = Column(String(64), nullable=True)
    detail = Column(String(512), nullable=True)
    created_at = Column(DateTime, nullable=False)
