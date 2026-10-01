from sqlalchemy import Column, DateTime, Integer, String

from src.config.database import Base


class HazardTicket(Base):
    __tablename__ = "hazard_ticket"

    id = Column(Integer, primary_key=True, autoincrement=True)
    result_id = Column(Integer, nullable=False, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    severity = Column(String(16), nullable=False, default="MEDIUM")
    owner_id = Column(Integer, nullable=True)
    deadline = Column(DateTime, nullable=True)
    # OPEN / RECTIFIED / VERIFIED / VOID_PENDING_REVIEW
    rectify_status = Column(String(32), nullable=False, default="OPEN", index=True)
    rectify_note = Column(String(256), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    voided_at = Column(DateTime, nullable=True)
    voided_by_outage_id = Column(Integer, nullable=True)
