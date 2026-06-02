from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.schemas.category import CategoryResponse, SubcategoryResponse, CategoryCreate
from app.models.problem_category import ProblemCategory
from app.models.problem_subcategory import ProblemSubcategory
from app.models.user import User
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    categories = db.query(ProblemCategory).options(
        joinedload(ProblemCategory.subcategories),
    ).filter(ProblemCategory.is_active == True).order_by(ProblemCategory.name).all()

    result = []
    for cat in categories:
        result.append(CategoryResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            icon=cat.icon,
            priority_default=cat.priority_default,
            is_active=cat.is_active,
            subcategories=[SubcategoryResponse(
                id=sc.id,
                category_id=sc.category_id,
                name=sc.name,
                description=sc.description,
                sort_order=sc.sort_order,
                is_active=sc.is_active,
            ) for sc in (cat.subcategories or []) if sc.is_active],
        ))
    return result


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    cat = ProblemCategory(
        name=data.name,
        description=data.description,
        icon=data.icon,
        priority_default=data.priority_default,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        icon=cat.icon,
        priority_default=cat.priority_default,
        is_active=cat.is_active,
        subcategories=[],
    )
