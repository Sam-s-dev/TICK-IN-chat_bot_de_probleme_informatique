from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SubcategoryResponse(BaseModel):
    id: int
    category_id: int
    name: str
    description: Optional[str] = None
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    priority_default: str
    is_active: bool
    subcategories: List[SubcategoryResponse] = []

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    priority_default: str = "medium"
