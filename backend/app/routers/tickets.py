from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, cast, Date
from typing import Optional
from datetime import date, datetime, timedelta

from app.database import get_db
from app.schemas.ticket import TicketCreate, TicketResponse, TicketStatusUpdate, TicketAssign
from app.models.ticket import Ticket
from app.models.user import User
from app.models.ticket_status_history import TicketStatusHistory
from app.dependencies import get_current_user, require_technician, require_admin
from app.services.ticket_service import create_ticket, change_ticket_status, create_notification

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_new_ticket(data: TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role_id != 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seuls les etudiants peuvent creer des tickets")
    ticket = create_ticket(db, current_user.id, data)
    db.refresh(ticket)
    return _to_response(ticket)


@router.get("/", response_model=dict)
def list_tickets(
    status_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Ticket).options(
        joinedload(Ticket.user),
        joinedload(Ticket.category),
        joinedload(Ticket.subcategory),
        joinedload(Ticket.room),
        joinedload(Ticket.status),
        joinedload(Ticket.technician),
    )
    if current_user.role_id == 3:
        query = query.filter(Ticket.user_id == current_user.id)
    elif current_user.role_id == 2:
        query = query.filter(Ticket.assigned_to == current_user.id)
    if status_id:
        query = query.filter(Ticket.status_id == status_id)
    if category_id:
        query = query.filter(Ticket.category_id == category_id)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if assigned_to and current_user.role_id == 1:
        query = query.filter(Ticket.assigned_to == assigned_to)
    total = query.count()
    tickets = query.order_by(desc(Ticket.created_at)).offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "tickets": [_to_response(t) for t in tickets]}


@router.get("/my-stats", response_model=dict)
def my_stats(db: Session = Depends(get_db), current_user: User = Depends(require_technician)):
    assigned = db.query(Ticket).filter(Ticket.assigned_to == current_user.id)
    today_start = date.today()
    encours = assigned.filter(Ticket.status_id.in_([2, 3, 4])).count()
    en_attente = assigned.filter(Ticket.status_id == 4).count()
    resolus_aujourdhui = assigned.filter(
        Ticket.status_id == 5,
        cast(Ticket.resolved_at, Date) == today_start,
    ).count()
    total_assignes = assigned.count()
    tickets_recents = assigned.order_by(desc(Ticket.created_at)).limit(5).all()
    return {
        "encours": encours,
        "en_attente": en_attente,
        "resolus_aujourdhui": resolus_aujourdhui,
        "total_assignes": total_assignes,
        "tickets": [_to_response(t) for t in tickets_recents],
    }


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).options(
        joinedload(Ticket.user),
        joinedload(Ticket.category),
        joinedload(Ticket.subcategory),
        joinedload(Ticket.room),
        joinedload(Ticket.status),
        joinedload(Ticket.technician),
    ).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    if current_user.role_id == 3 and ticket.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise a ce ticket")
    return _to_response(ticket)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, data: TicketStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_technician)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    ticket = change_ticket_status(db, ticket, data.status_id, current_user.id, data.comment, data.resolution_notes)
    create_notification(db, ticket.user_id, ticket.id, "status_change",
                        f"Statut mis a jour",
                        f"Votre ticket {ticket.ticket_number} est maintenant '{ticket.status.label}'")
    db.refresh(ticket)
    return _to_response(ticket)


@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(ticket_id: int, data: TicketAssign, db: Session = Depends(get_db), current_user: User = Depends(require_technician)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    tech = db.query(User).filter(User.id == data.technician_id).first()
    if not tech:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technicien introuvable")
    if ticket.status_id == 1:
        comment = f"Assigné à {tech.first_name} {tech.last_name}" if tech else "Assigné à un technicien"
        ticket = change_ticket_status(db, ticket, 2, current_user.id, comment)
    ticket.assigned_to = data.technician_id
    db.commit()
    create_notification(db, ticket.user_id, ticket.id, "assignment",
                        "Ticket pris en charge",
                        f"Votre ticket {ticket.ticket_number} a ete assigne a {tech.first_name} {tech.last_name}")
    if data.technician_id != current_user.id:
        create_notification(db, data.technician_id, ticket.id, "new_ticket",
                            f"Nouveau ticket assigne",
                            f"Ticket {ticket.ticket_number} ({ticket.description[:80] if ticket.description else 'Sans description'}) vous a ete assigne")
    db.refresh(ticket)
    return _to_response(ticket)


@router.delete("/{ticket_id}", status_code=status.HTTP_200_OK)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    db.delete(ticket)
    db.commit()
    return {"detail": "Ticket supprime avec succes", "ticket_id": ticket_id, "ticket_number": ticket.ticket_number}


def _to_response(t: Ticket) -> TicketResponse:
    return TicketResponse(
        id=t.id,
        ticket_number=t.ticket_number,
        user_id=t.user_id,
        user_name=f"{t.user.first_name} {t.user.last_name}" if t.user else "",
        category_id=t.category_id,
        category_name=t.category.name if t.category else "",
        subcategory_id=t.subcategory_id,
        subcategory_name=t.subcategory.name if t.subcategory else None,
        room_id=t.room_id,
        room_name=t.room.name if t.room else "",
        building_name=t.room.building.name if t.room and t.room.building else "",
        workstation_number=t.workstation_number,
        description=t.description,
        status_id=t.status_id,
        status_label=t.status.label if t.status else "",
        assigned_to=t.assigned_to,
        technician_name=f"{t.technician.first_name} {t.technician.last_name}" if t.technician else None,
        priority=t.priority,
        source=t.source,
        sla_deadline=t.sla_deadline,
        escalated_at=t.escalated_at,
        resolution_notes=t.resolution_notes,
        created_at=t.created_at,
        updated_at=t.updated_at,
        resolved_at=t.resolved_at,
    )
