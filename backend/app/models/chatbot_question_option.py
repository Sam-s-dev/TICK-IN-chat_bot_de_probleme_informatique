from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class ChatbotQuestionOption(Base):
    __tablename__ = "chatbot_question_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("chatbot_questions.id", ondelete="CASCADE"), nullable=False)
    option_text = Column(String(255), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    question = relationship("ChatbotQuestion", lazy="joined")
