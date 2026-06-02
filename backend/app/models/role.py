from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
