from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoomResponse(BaseModel):
    id: int
    building_id: Optional[int] = None
    building_name: Optional[str] = None
    name: str
    floor: Optional[int] = None
    room_type: str
    is_active: bool

    class Config:
        from_attributes = True


class RoomCreate(BaseModel):
    building_name: Optional[str] = None
    name: str
    floor: Optional[int] = None
    room_type: str = "other"


class BuildingResponse(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        from_attributes = True
