import threading
import time
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.ticket import Ticket
from app.models.notification import Notification
from app.models.system_config import SystemConfig
from app.models.user import User

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 300


def get_config_int(db: Session, key: str, default: int) -> int:
    config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if config and config.config_value:
        try:
            return int(config.config_value)
        except ValueError:
            return default
    return default


def check_pending_tickets():
    db = SessionLocal()
    try:
        reminder_hours = get_config_int(db, "reminder_hours", 24)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=reminder_hours)

        pending = db.query(Ticket).filter(
            Ticket.status_id == 1,
            Ticket.created_at <= cutoff,
        ).all()

        for ticket in pending:
            existing = db.query(Notification).filter(
                Notification.ticket_id == ticket.id,
                Notification.type == "reminder",
            ).first()
            if existing:
                continue

            admins = db.query(User).filter(User.role_id == 1).all()
            for admin in admins:
                notif = Notification(
                    user_id=admin.id,
                    ticket_id=ticket.id,
                    type="reminder",
                    title="Ticket en attente",
                    message=f"Le ticket {ticket.ticket_number} ({ticket.description[:80]}...) n'est pas encore pris en charge depuis plus de {reminder_hours}h.",
                )
                db.add(notif)

        db.commit()

        if pending:
            logger.info(f"Reminder: {len(pending)} ticket(s) en attente signalé(s)")
    except Exception as e:
        logger.error(f"Erreur dans le rappel périodique: {e}")
        db.rollback()
    finally:
        db.close()


def reminder_loop():
    while True:
        check_pending_tickets()
        time.sleep(CHECK_INTERVAL_SECONDS)


def start_reminder_service():
    thread = threading.Thread(target=reminder_loop, daemon=True)
    thread.start()
    logger.info("Service de rappel périodique démarré")
