from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ticket import EvaluationCreate, EvaluationResponse
from app.models.ticket import Ticket
from app.models.evaluation import Evaluation
from app.models.user import User
from app.dependencies import get_current_user
from app.models.notification import Notification

router = APIRouter(prefix="/api/tickets/{ticket_id}/evaluation", tags=["Evaluations"])


@router.post("/", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
def create_evaluation(ticket_id: int, data: EvaluationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seul le createur du ticket peut evaluer")
    if ticket.status_id != 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le ticket doit etre resolu pour etre evalue")
    existing = db.query(Evaluation).filter(Evaluation.ticket_id == ticket_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce ticket a deja ete evalue")
    if data.rating not in (1, 2, 3):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La note doit etre 1, 2 ou 3")
    eval = Evaluation(
        ticket_id=ticket_id,
        user_id=current_user.id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(eval)
    db.commit()
    db.refresh(eval)

    stars = {1: "1/3", 2: "2/3", 3: "3/3"}
    label = stars.get(data.rating, "?/3")
    if ticket.assigned_to:
        notif = Notification(
            user_id=ticket.assigned_to,
            ticket_id=ticket_id,
            type="evaluation",
            title="Nouvelle evaluation",
            message=f"Ticket {ticket.ticket_number}: {label} {(data.comment or '')[:200]}",
        )
        db.add(notif)
    admins = db.query(User).filter(User.role_id == 1, User.is_active == True).all()
    for admin in admins:
        notif = Notification(
            user_id=admin.id,
            ticket_id=ticket_id,
            type="evaluation",
            title=f"Evaluation par {current_user.first_name} {current_user.last_name}",
            message=f"Ticket {ticket.ticket_number}: {label} {(data.comment or '')[:200]}",
        )
        db.add(notif)
    db.commit()
    return EvaluationResponse(
        id=eval.id,
        ticket_id=eval.ticket_id,
        user_id=eval.user_id,
        rating=eval.rating,
        comment=eval.comment,
        created_at=eval.created_at,
    )


@router.get("/", response_model=EvaluationResponse)
def get_evaluation(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket introuvable")
    if current_user.role_id == 3 and ticket.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces non autorise")
    eval = db.query(Evaluation).filter(Evaluation.ticket_id == ticket_id).first()
    if not eval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aucune evaluation pour ce ticket")
    return EvaluationResponse(
        id=eval.id,
        ticket_id=eval.ticket_id,
        user_id=eval.user_id,
        rating=eval.rating,
        comment=eval.comment,
        created_at=eval.created_at,
    )
