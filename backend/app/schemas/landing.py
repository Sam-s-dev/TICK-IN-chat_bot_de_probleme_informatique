from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TestimonialResponse(BaseModel):
    id: int
    name: str
    role: str
    text: str
    stars: int

    class Config:
        from_attributes = True


class FaqResponse(BaseModel):
    id: int
    question: str
    answer: str
    sort_order: int

    class Config:
        from_attributes = True
