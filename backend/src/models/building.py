"""建筑楼栋 ORM 模型。"""
from sqlalchemy import Column, Integer, String

from src.database import Base


class Building(Base):
    __tablename__ = "building"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    campus = Column(String(128), nullable=False, default="")
    floor_count = Column(Integer, nullable=False, default=1)
    fire_grade = Column(String(32), nullable=False, default="SECOND")
    manager_id = Column(Integer, nullable=True)
    address_code = Column(String(64), nullable=False, default="")
