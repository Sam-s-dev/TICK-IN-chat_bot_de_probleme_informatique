import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc

from app.models.ticket import Ticket
from app.models.user import User
from app.models.ticket_status_history import TicketStatusHistory
from app.models.notification import Notification
from app.services.ws_manager import manager, _run_async
from app.services.ai_service import ai_assign_technician


def _find_least_busy_technician(db: Session) -> User | None:
    techs = db.query(User).filter(User.role_id == 2, User.is_active == True).all()
    if not techs:
        return None
    tech_load = []
    for t in techs:
        count = db.query(sqlfunc.count(Ticket.id)).filter(
            Ticket.assigned_to == t.id,
            Ticket.status_id.in_([2, 3, 4]),
        ).scalar()
        tech_load.append((count, t))
    tech_load.sort(key=lambda x: x[0])
    return tech_load[0][1]


def generate_ticket_number(db: Session) -> str:
    prefix = "TKT"
    config = db.query(SystemConfig).filter(SystemConfig.config_key == "ticket_prefix").first()
    if config:
        prefix = config.config_value
    last = db.query(Ticket).order_by(Ticket.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"{prefix}-{next_num:05d}"


def get_sla_deadline(db: Session, priority: str) -> datetime:
    key = f"sla_hours_{priority}"
    config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    hours = int(config.config_value) if config else 48
    return datetime.now(timezone.utc) + timedelta(hours=hours)


def create_ticket(db: Session, user_id: int, data, source: str = "dashboard") -> Ticket:
    ticket = Ticket(
        ticket_number=generate_ticket_number(db),
        user_id=user_id,
        category_id=data.category_id,
        subcategory_id=data.subcategory_id,
        room_id=data.room_id,
        workstation_number=data.workstation_number,
        description=data.description,
        status_id=2,
        priority=data.priority,
        source=source,
        sla_deadline=get_sla_deadline(db, data.priority),
    )

    db.add(ticket)
    db.flush()

    history = TicketStatusHistory(
        ticket_id=ticket.id,
        from_status=None,
        to_status=ticket.status_id,
        changed_by=user_id,
        comment="Creation du ticket",
    )
    db.add(history)

    # AI assignment with fallback
    tech_id = ai_assign_technician(db, data.category_id, data.subcategory_id, data.description or "", data.priority)
    if tech_id is None:
        tech = _find_least_busy_technician(db)
        tech_id = tech.id if tech else None

    if tech_id:
        ticket.assigned_to = tech_id
        tech = db.query(User).filter(User.id == tech_id).first()
        create_notification(db, tech_id, ticket.id, "new_ticket",
                            "Nouveau ticket assigne par IA",
                            f"Ticket {ticket.ticket_number}: {data.description[:100] if data.description else 'Pas de description'}")
        create_notification(db, user_id, ticket.id, "status_change",
                            "Ticket cree et assigne",
                            f"Votre ticket {ticket.ticket_number} a ete cree et assigne a {tech.first_name} {tech.last_name}")
    else:
        create_notification(db, user_id, ticket.id, "status_change",
                            "Ticket cree",
                            f"Votre ticket {ticket.ticket_number} a ete cree. Un administrateur va l assigner a un technicien.")

    student = db.query(User).filter(User.id == user_id).first()
    if student:
        admins = db.query(User).filter(User.role_id == 1, User.is_active == True).all()
        for admin in admins:
            create_notification(db, admin.id, ticket.id, "new_ticket",
                                f"Nouveau ticket de {student.first_name} {student.last_name}",
                                f"Ticket {ticket.ticket_number}: {data.description[:100] if data.description else 'Pas de description'}")

    db.commit()
    db.refresh(ticket)
    return ticket


def change_ticket_status(db: Session, ticket: Ticket, status_id: int, user_id: int, comment: str = None, resolution_notes: str = None) -> Ticket:
    from_status = ticket.status_id
    ticket.status_id = status_id
    if resolution_notes:
        ticket.resolution_notes = resolution_notes
    if status_id == 5:
        ticket.resolved_at = datetime.now(timezone.utc)
        ticket.closed_by = user_id

    history = TicketStatusHistory(
        ticket_id=ticket.id,
        from_status=from_status,
        to_status=status_id,
        changed_by=user_id,
        comment=comment,
    )
    db.add(history)
    db.commit()
    db.refresh(ticket)
    return ticket


def create_notification(db: Session, user_id: int, ticket_id: int, notif_type: str, title: str, message: str = None):
    notif = Notification(
        user_id=user_id,
        ticket_id=ticket_id,
        type=notif_type,
        title=title,
        message=message,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    _push_notification_ws(user_id, {
        "type": "notification",
        "notification": {
            "id": notif.id,
            "ticket_id": ticket_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "is_read": False,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
        }
    })


def _push_notification_ws(user_id: int, data: dict):
    _run_async(manager.send_to_user(user_id, data))
