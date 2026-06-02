from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
