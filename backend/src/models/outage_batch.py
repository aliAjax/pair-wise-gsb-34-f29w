from sqlalchemy import Column, DateTime, Integer, String, Text

from src.config.database import Base


class OutageBatch(Base):
    """一次提交的停用批次：用于“写入失败后恢复”。

    PENDING 条目表示当时没写成功，reactivate/resume 时只处理这些条目，
    已占名额（CONFIRMED 条目）不重复也不丢失。
    """

    __tablename__ = "outage_batch"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submitted_by = Column(Integer, nullable=False)
    submitted_at = Column(DateTime, nullable=False)
    # PARTIAL_FAILED / COMPLETED / RESUMED
    status = Column(String(32), nullable=False, default="PARTIAL_FAILED", index=True)
    note = Column(String(256), nullable=True)
    # 模拟写入失败的设备序号（1 基），用于演示续传；实际落库的条目不再重放
    fail_device_codes = Column(Text, nullable=False, default="")
