from sqlalchemy import Column, Integer, String

from src.config.database import Base


class Building(Base):
    __tablename__ = "building"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    campus = Column(String(64), nullable=False)
    floor_count = Column(Integer, nullable=False, default=1)
    fire_grade = Column(String(32), nullable=False, default="二级")
    manager_id = Column(Integer, nullable=True)
    address_code = Column(String(32), nullable=True)
