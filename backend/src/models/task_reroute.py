from sqlalchemy import Column, Integer, String, UniqueConstraint

from src.config.database import Base


class TaskReroute(Base):
    """停用冲突下巡检任务对设备的实际占用关系。

    relation=ORIGINAL 保留原任务关系；BACKUP 是改派到备用设备；
    QUEUED 表示备用容量不足排队待补检。
    唯一约束 (task_id, outage_id, device_id, relation) 保证续传幂等：
    已占名额不重复也不丢失。
    """

    __tablename__ = "task_reroute"
    __table_args__ = (
        UniqueConstraint(
            "task_id", "outage_id", "device_id", "relation",
            name="uq_reroute_task_outage_device_relation",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)
    outage_id = Column(Integer, nullable=True, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    backup_device_id = Column(Integer, nullable=True, index=True)
    # ORIGINAL / BACKUP / QUEUED
    relation = Column(String(16), nullable=False, default="ORIGINAL", index=True)
    note = Column(String(256), nullable=True)
