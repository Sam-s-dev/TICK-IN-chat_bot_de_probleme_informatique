import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import FileResponse

from app.database import get_db
from app.models.ticket import Ticket
from app.models.ticket_attachment import TicketAttachment
from app.models.ticket_message import TicketMessage
from app.models.notification import Notification
from app.models.user import User
from app.models.system_config import SystemConfig
from app.dependencies import get_current_user
from app.services.auth_service import decode_access_token
from app.services.ws_manager import manager, _run_async

router = APIRouter(prefix="/api/uploads", tags=["Fichiers joints"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

AUDIO_DIR = os.path.join(UPLOAD_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


def get_config_str(db: Session, key: str, default: str) -> str:
    config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    return config.config_value if config and config.config_value else default


def get_config_int(db: Session, key: str, default: int) -> int:
    config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if config and config.config_value:
        try:
            return int(config.config_value)
        except ValueError:
            return default
    return default


@router.post("/tickets/{ticket_id}")
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    message_type: str = Form("file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    if ticket.user_id != current_user.id and current_user.role_id > 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez pas joindre de fichier a ce ticket")

    max_size_mb = get_config_int(db, "max_photo_size_mb", 2)
    max_size_bytes = max_size_mb * 1024 * 1024
    allowed_types = get_config_str(db, "allowed_mime_types", "image/jpeg,image/png,image/gif,application/pdf")
    allowed_list = [t.strip() for t in allowed_types.split(",")]

    if message_type == "audio":
        allowed_list = ["audio/webm", "audio/ogg", "audio/wav", "audio/mp4", "audio/mpeg", "audio/x-m4a", "audio/aac"]
        if not max_size_bytes or max_size_bytes < 10 * 1024 * 1024:
            max_size_bytes = 10 * 1024 * 1024

    content = await file.read()

    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop volumineux. Maximum: {max_size_mb} Mo",
        )

    ct = (file.content_type or "").lower()
    if not any(ct.startswith(a) or ct == a for a in allowed_list):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Type MIME '{file.content_type}' non autorise",
        )

    ext = os.path.splitext(file.filename)[1] if file.filename else ".webm"
    stored_name = f"{uuid.uuid4().hex}{ext}"

    if message_type == "audio":
        file_path = os.path.join(AUDIO_DIR, stored_name)
    else:
        file_path = os.path.join(UPLOAD_DIR, stored_name)

    with open(file_path, "wb") as f:
        f.write(content)

    attachment = TicketAttachment(
        ticket_id=ticket_id,
        file_name=file.filename or stored_name,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.flush()

    msg_label = "Message vocal" if message_type == "audio" else (file.filename or "Fichier")
    msg = TicketMessage(
        ticket_id=ticket_id,
        sender_id=current_user.id,
        message=msg_label,
        message_type=message_type,
        attachment_id=attachment.id,
    )
    db.add(msg)
    db.commit()
    db.refresh(attachment)
    db.refresh(msg)

    notif_user_id = ticket.assigned_to if ticket.assigned_to and current_user.id != ticket.assigned_to else ticket.user_id
    if notif_user_id and notif_user_id != current_user.id:
        notif = Notification(
            user_id=notif_user_id,
            ticket_id=ticket_id,
            type="new_message",
            title=f"Nouveau message de {current_user.first_name} {current_user.last_name}" if current_user.role_id == 3 else "Nouveau message de votre technicien",
            message=msg_label,
        )
        db.add(notif)
        db.commit()
        _run_async(manager.send_to_user(notif_user_id, {
            "type": "notification",
            "notification": {
                "id": notif.id,
                "ticket_id": ticket_id,
                "type": "new_message",
                "title": notif.title,
                "message": msg_label,
                "is_read": False,
                "created_at": notif.created_at.isoformat() if notif.created_at else None,
            }
        }))
        _run_async(manager.send_to_user(notif_user_id, {
            "type": "new_message",
            "message": {
                "id": msg.id,
                "ticket_id": ticket_id,
                "sender_id": current_user.id,
                "sender_name": f"{current_user.first_name} {current_user.last_name}",
                "message": msg_label,
                "message_type": message_type,
                "is_deleted": False,
                "attachment_id": attachment.id,
                "attachment_url": f"/api/uploads/files/{attachment.id}",
                "attachment_name": attachment.file_name,
                "attachment_type": attachment.mime_type,
                "public_url": None,
                "is_read": False,
                "created_at": attachment.created_at.isoformat() if attachment.created_at else None,
            }
        }))

    return {
        "id": attachment.id,
        "file_name": attachment.file_name,
        "file_size": attachment.file_size,
        "mime_type": attachment.mime_type,
        "message_type": message_type,
        "message_id": msg.id,
        "created_at": attachment.created_at.isoformat() if attachment.created_at else None,
    }


@router.get("/tickets/{ticket_id}")
def list_attachments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    if ticket.user_id != current_user.id and current_user.role_id > 2:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces refuse")

    attachments = db.query(TicketAttachment).filter(
        TicketAttachment.ticket_id == ticket_id
    ).order_by(TicketAttachment.created_at.desc()).all()

    return [
        {
            "id": a.id,
            "file_name": a.file_name,
            "file_size": a.file_size,
            "mime_type": a.mime_type,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "uploaded_by": a.uploader.first_name + " " + a.uploader.last_name if a.uploader else "Inconnu",
        }
        for a in attachments
    ]


@router.get("/files/{attachment_id}")
def download_attachment(
    attachment_id: int,
    token: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attachment = db.query(TicketAttachment).filter(TicketAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable")

    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable sur le disque")

    media = attachment.mime_type or "application/octet-stream"
    return FileResponse(
        attachment.file_path,
        media_type=media,
        filename=attachment.file_name,
    )


@router.get("/public/{attachment_id}")
def download_attachment_public(
    attachment_id: int,
    token: str = Query(None),
    db: Session = Depends(get_db),
):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requis")
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")

    attachment = db.query(TicketAttachment).filter(TicketAttachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable")
    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fichier introuvable sur le disque")

    media = attachment.mime_type or "application/octet-stream"
    return FileResponse(
        attachment.file_path,
        media_type=media,
        filename=attachment.file_name,
    )
