from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class ChatbotQuestion(Base):
    __tablename__ = "chatbot_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("problem_categories.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("problem_subcategories.id"), nullable=True)
    question_text = Column(String(500), nullable=False)
    question_type = Column(String(20), nullable=False, default="text")
    sort_order = Column(Integer, nullable=False, default=0)
    is_required = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    category = relationship("ProblemCategory", lazy="joined")
    subcategory = relationship("ProblemSubcategory", lazy="joined")
