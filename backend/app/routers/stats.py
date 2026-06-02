from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta, date

from app.database import get_db
from app.models.ticket import Ticket
from app.models.evaluation import Evaluation
from app.models.user import User
from app.models.problem_category import ProblemCategory
from app.models.ticket_status import TicketStatus
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/stats", tags=["Statistiques"])


@router.get("/dashboard")
def get_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status_id < 5).count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status_id == 5).count()
    unassigned = db.query(Ticket).filter(Ticket.status_id == 1).count()
    avg_rating = db.query(func.avg(Evaluation.rating)).scalar() or 0

    total_users = db.query(User).count()
    admin_count = db.query(User).filter(User.role_id == 1).count()
    tech_count = db.query(User).filter(User.role_id == 2).count()
    student_count = db.query(User).filter(User.role_id == 3).count()

    tickets_by_status = db.query(
        TicketStatus.name,
        func.count(Ticket.id).label("count"),
    ).join(Ticket, Ticket.status_id == TicketStatus.id
    ).group_by(TicketStatus.name, TicketStatus.id
    ).order_by(TicketStatus.id).all()

    tickets_by_category = db.query(
        ProblemCategory.name,
        func.count(Ticket.id).label("count"),
    ).join(Ticket, Ticket.category_id == ProblemCategory.id
    ).group_by(ProblemCategory.name).all()

    tickets_per_day = db.query(
        cast(Ticket.created_at, Date).label("day"),
        func.count(Ticket.id).label("count"),
    ).filter(Ticket.created_at >= seven_days_ago
    ).group_by(cast(Ticket.created_at, Date)
    ).order_by("day").all()

    top_technicians = db.query(
        User.first_name,
        User.last_name,
        func.count(Ticket.id).label("resolved"),
    ).join(Ticket, Ticket.assigned_to == User.id
    ).filter(Ticket.status_id == 5, User.role_id == 2
    ).group_by(User.id, User.first_name, User.last_name
    ).order_by(func.count(Ticket.id).desc()
    ).limit(5).all()

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "unassigned_tickets": unassigned,
        "average_rating": round(float(avg_rating), 2),
        "total_users": total_users,
        "users_by_role": {
            "admin": admin_count,
            "technicien": tech_count,
            "etudiant": student_count,
        },
        "tickets_by_status": [{"name": s, "count": c} for s, c in tickets_by_status],
        "tickets_by_category": [{"name": cat, "count": c} for cat, c in tickets_by_category],
        "tickets_per_day": [{"day": str(d), "count": c} for d, c in tickets_per_day],
        "top_technicians": [{"name": f"{f} {l}", "resolved": r} for f, l, r in top_technicians],
    }
