from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import timedelta

from app.database import get_db
from app.schemas.ticket import MessageSend, MessageResponse
from app.models.ticket import Ticket
from app.models.ticket_message import TicketMessage
from app.models.ticket_attachment import TicketAttachment
from app.models.user import User
from app.models.notification import Notification
from app.dependencies import get_current_user
from app.services.auth_service import create_access_token
from app.services.ws_manager import manager, _run_async

router = APIRouter(prefix="/api/tickets/{ticket_id}/messages", tags=["Messages"])


@router.get("/", response_model=List[MessageResponse])
def list_messages(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    if current_user.role_id == 3 and ticket.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise")
    messages = db.query(TicketMessage).options(
        joinedload(TicketMessage.sender),
        joinedload(TicketMessage.attachment),
    ).filter(
        TicketMessage.ticket_id == ticket_id
    ).order_by(TicketMessage.created_at).all()
    if current_user.role_id != 3:
        for m in messages:
            if m.sender_id == ticket.user_id:
                m.is_read = True
        db.commit()
    return [_msg_to_response(m) for m in messages]


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(ticket_id: int, data: MessageSend, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    if current_user.role_id == 3 and ticket.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise")
    if current_user.role_id == 2 and ticket.assigned_to != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ce ticket ne vous est pas assigne")
    if data.attachment_id:
        att = db.query(TicketAttachment).filter(TicketAttachment.id == data.attachment_id).first()
        if not att or att.ticket_id != ticket_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier joint introuvable")
    msg = TicketMessage(
        ticket_id=ticket_id,
        sender_id=current_user.id,
        message=data.message,
        message_type=data.message_type,
        attachment_id=data.attachment_id,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    notif_user_id = None
    if current_user.role_id == 3 and ticket.assigned_to:
        notif_user_id = ticket.assigned_to
        title = f"Nouveau message de {current_user.first_name} {current_user.last_name}"
    elif current_user.role_id == 2:
        notif_user_id = ticket.user_id
        title = "Nouveau message de votre technicien"

    if notif_user_id:
        notif = Notification(
            user_id=notif_user_id,
            ticket_id=ticket_id,
            type="new_message",
            title=title,
            message=data.message[:200] if data.message else "Fichier partage",
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        _run_async(manager.send_to_user(notif_user_id, {
            "type": "notification",
            "notification": {
                "id": notif.id,
                "ticket_id": ticket_id,
                "type": "new_message",
                "title": title,
                "message": data.message[:200] if data.message else "Fichier partage",
                "is_read": False,
                "created_at": notif.created_at.isoformat() if notif.created_at else None,
            }
        }))

    resp = _msg_to_response(msg)
    # Push message via WS to all chat participants
    for uid in [ticket.user_id, ticket.assigned_to]:
        if uid and uid != current_user.id:
            _run_async(manager.send_to_user(uid, {"type": "new_message", "message": resp.model_dump() if hasattr(resp, 'model_dump') else resp.__dict__}))

    return resp


@router.delete("/{message_id}", status_code=status.HTTP_200_OK)
def delete_message(ticket_id: int, message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    msg = db.query(TicketMessage).filter(TicketMessage.id == message_id, TicketMessage.ticket_id == ticket_id).first()
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message introuvable")
    if msg.sender_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez supprimer que vos propres messages")
    msg.is_deleted = True
    msg.message = "Message supprime"
    db.commit()
    return {"detail": "Message supprime"}


@router.delete("/", status_code=status.HTTP_200_OK)
def delete_conversation(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    if current_user.role_id == 3 and ticket.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise")
    if current_user.role_id == 2 and ticket.assigned_to != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ce ticket ne vous est pas assigne")
    messages = db.query(TicketMessage).filter(TicketMessage.ticket_id == ticket_id).all()
    for m in messages:
        m.is_deleted = True
        m.message = "Message supprime"
    db.commit()
    return {"detail": "Conversation supprimee"}


def _msg_to_response(m: TicketMessage) -> MessageResponse:
    att_url = None
    att_name = None
    att_type = None
    public_url = None
    if m.attachment:
        att_url = f"/api/uploads/files/{m.attachment.id}"
        att_name = m.attachment.file_name
        att_type = m.attachment.mime_type
        token = create_access_token({"sub": str(m.attachment.id), "type": "attachment"}, timedelta(hours=1))
        public_url = f"/api/uploads/public/{m.attachment.id}?token={token}"
    return MessageResponse(
        id=m.id,
        ticket_id=m.ticket_id,
        sender_id=m.sender_id,
        sender_name=f"{m.sender.first_name} {m.sender.last_name}" if m.sender else "",
        message=m.message if not m.is_deleted else "Ce message a ete supprime",
        message_type=m.message_type,
        is_deleted=m.is_deleted,
        attachment_id=m.attachment_id,
        attachment_url=att_url,
        attachment_name=att_name,
        attachment_type=att_type,
        public_url=public_url,
        is_read=m.is_read,
        created_at=m.created_at,
    )
