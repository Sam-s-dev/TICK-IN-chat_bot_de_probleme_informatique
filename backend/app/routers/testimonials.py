from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.landing import TestimonialResponse
from app.models.testimonial import Testimonial

router = APIRouter(prefix="/api/testimonials", tags=["Temoignages"])


@router.get("/", response_model=List[TestimonialResponse])
def list_testimonials(db: Session = Depends(get_db)):
    return db.query(Testimonial).filter(Testimonial.is_active == True).order_by(Testimonial.id).all()
