from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, default="text")
    is_deleted = Column(Boolean, nullable=False, default=False)
    attachment_id = Column(Integer, ForeignKey("ticket_attachments.id", ondelete="SET NULL"), nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    ticket = relationship("Ticket", lazy="joined")
    sender = relationship("User", lazy="joined")
    attachment = relationship("TicketAttachment", lazy="joined")
