from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, func
from app.database import Base


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    email_notifications = Column(Boolean, nullable=False, default=True)
    in_app_notifications = Column(Boolean, nullable=False, default=True)
    sms_notifications = Column(Boolean, nullable=False, default=False)
    notify_new_ticket = Column(Boolean, nullable=False, default=True)
    notify_status_change = Column(Boolean, nullable=False, default=True)
    notify_assignment = Column(Boolean, nullable=False, default=True)
    notify_reminder = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
