from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class TicketStatusHistory(Base):
    __tablename__ = "ticket_status_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    from_status = Column(Integer, ForeignKey("ticket_statuses.id"), nullable=True)
    to_status = Column(Integer, ForeignKey("ticket_statuses.id"), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    ticket = relationship("Ticket", lazy="joined")
    from_status_rel = relationship("TicketStatus", foreign_keys=[from_status], lazy="joined")
    to_status_rel = relationship("TicketStatus", foreign_keys=[to_status], lazy="joined")
    changer = relationship("User", lazy="joined")
