from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
import json

from app.database import get_db
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.models.user import User
from app.models.ticket import Ticket
from app.models.audit_log import AuditLog
from app.services.auth_service import hash_password
from app.dependencies import get_current_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])


@router.get("/", response_model=List[UserResponse])
def list_users(role_id: int = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    query = db.query(User)
    if role_id:
        query = query.filter(User.role_id == role_id)
    users = query.order_by(User.role_id, User.last_name).all()
    return [UserResponse(
        id=u.id,
        role_id=u.role_id,
        role_name=u.role.name,
        student_id=u.student_id,
        first_name=u.first_name,
        last_name=u.last_name,
        email=u.email,
        phone=u.phone,
        is_active=u.is_active,
        last_login_at=u.last_login_at,
        created_at=u.created_at,
    ) for u in users]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    existing = db.query(User).filter(User.email == data.email).first()
    if not existing and data.student_id:
        existing = db.query(User).filter(User.student_id == data.student_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Un utilisateur avec cet email ou ce numero etudiant existe deja")
    user = User(
        role_id=data.role_id,
        student_id=data.student_id,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        created_by=admin.id,
    )
    db.add(user)
    db.flush()
    log = AuditLog(
        user_id=admin.id,
        action="create",
        entity_type="user",
        entity_id=user.id,
        new_values=json.dumps({"role": user.role.name, "nom": f"{user.first_name} {user.last_name}"}),
    )
    db.add(log)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        role_id=user.role_id,
        role_name=user.role.name,
        student_id=user.student_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    old_values = json.dumps({"is_active": user.is_active})
    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.email is not None:
        user.email = data.email
    if data.phone is not None:
        user.phone = data.phone
    if data.is_active is not None:
        user.is_active = data.is_active
    log = AuditLog(
        user_id=admin.id,
        action="update",
        entity_type="user",
        entity_id=user.id,
        old_values=old_values,
        new_values=json.dumps({"is_active": user.is_active}),
    )
    db.add(log)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        role_id=user.role_id,
        role_name=user.role.name,
        student_id=user.student_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@router.get("/technicians")
def list_technicians(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    techs = db.query(User).filter(User.role_id == 2, User.is_active == True).order_by(User.last_name).all()
    result = []
    for t in techs:
        open_count = db.query(Ticket).filter(
            Ticket.assigned_to == t.id,
            Ticket.status_id.in_([1, 2, 3, 4]),
        ).count()
        total_tickets = db.query(Ticket).filter(Ticket.assigned_to == t.id).count()
        max_load = 5
        load_pct = min(int((open_count / max_load) * 100), 100) if max_load > 0 else 0
        status = "disponible" if load_pct < 50 else ("occupe" if load_pct < 80 else "sature")
        result.append({
            "id": t.id,
            "first_name": t.first_name,
            "last_name": t.last_name,
            "email": t.email,
            "open_tickets": open_count,
            "total_tickets": total_tickets,
            "load_pct": load_pct,
            "status": status,
        })
    return result
