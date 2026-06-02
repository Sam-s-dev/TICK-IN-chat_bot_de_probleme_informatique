from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(String(20), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("problem_categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("problem_subcategories.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    workstation_number = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status_id = Column(Integer, ForeignKey("ticket_statuses.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    priority = Column(String(10), nullable=False, default="medium")
    source = Column(String(20), nullable=False, default="chatbot")
    sla_deadline = Column(DateTime, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    closed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_duplicate_of = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    reminder_sent = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id], lazy="joined")
    category = relationship("ProblemCategory", lazy="joined")
    subcategory = relationship("ProblemSubcategory", lazy="joined")
    room = relationship("Room", lazy="joined")
    status = relationship("TicketStatus", lazy="joined")
    technician = relationship("User", foreign_keys=[assigned_to], lazy="joined")
    closer = relationship("User", foreign_keys=[closed_by], lazy="joined")
