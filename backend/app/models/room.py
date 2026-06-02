from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    building_name = Column(String(100), nullable=True)
    name = Column(String(100), nullable=False)
    floor = Column(Integer, nullable=True)
    room_type = Column(String(50), nullable=False, default="other")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    building = relationship("Building", lazy="joined")
