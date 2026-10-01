"""审计日志：所有写操作留痕。"""
from sqlalchemy import Column, DateTime, Integer, String, Text

from src.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor = Column(String(64), nullable=False, default="system")
    action = Column(String(128), nullable=False)
    target_type = Column(String(64), nullable=False)
    target_id = Column(String(64), nullable=False, default="")
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, index=True)
