from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class ProblemCategory(Base):
    __tablename__ = "problem_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    priority_default = Column(String(10), nullable=False, default="medium")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    subcategories = relationship("ProblemSubcategory", lazy="joined", order_by="ProblemSubcategory.sort_order")
