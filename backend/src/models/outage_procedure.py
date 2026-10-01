"""复役手续。手续没补齐的设备不能回到正常。"""
from sqlalchemy import Column, DateTime, Integer, String

from src.database import Base


class OutageProcedure(Base):
    __tablename__ = "outage_procedure"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, nullable=False, index=True)
    window_id = Column(Integer, nullable=False, index=True)
    procedure_type = Column(String(32), nullable=False)
    completed = Column(Integer, nullable=False, default=0)
    doc_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=True)
