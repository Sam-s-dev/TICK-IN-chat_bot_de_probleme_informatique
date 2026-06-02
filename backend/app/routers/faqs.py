from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.landing import FaqResponse
from app.models.faq import Faq

router = APIRouter(prefix="/api/faqs", tags=["FAQ"])


@router.get("/", response_model=List[FaqResponse])
def list_faqs(db: Session = Depends(get_db)):
    return db.query(Faq).filter(Faq.is_active == True).order_by(Faq.sort_order).all()
