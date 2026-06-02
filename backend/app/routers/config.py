from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.system_config import SystemConfig
from app.models.user import User
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/config", tags=["Configuration"])


@router.get("/")
def list_config(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    configs = db.query(SystemConfig).order_by(SystemConfig.config_key).all()
    return [{"key": c.config_key, "value": c.config_value, "description": c.description} for c in configs]


@router.put("/{config_key}")
def update_config(config_key: str, data: dict, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration introuvable")
    config.config_value = data["value"]
    config.updated_by = admin.id
    db.commit()
    return {"message": "Configuration mise à jour", "key": config_key, "value": data["value"]}
