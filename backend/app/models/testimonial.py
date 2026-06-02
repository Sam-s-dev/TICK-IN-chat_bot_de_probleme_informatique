from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.database import Base


class Testimonial(Base):
    __tablename__ = "testimonials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    stars = Column(Integer, nullable=False, default=5)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
