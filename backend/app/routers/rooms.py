from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.schemas.room import RoomResponse, RoomCreate, BuildingResponse
from app.models.room import Room
from app.models.building import Building
from app.models.user import User
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/rooms", tags=["Salles"])


@router.get("/buildings", response_model=List[BuildingResponse])
def list_buildings(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    buildings = db.query(Building).all()
    return [BuildingResponse(id=b.id, name=b.name, code=b.code) for b in buildings]


@router.get("/", response_model=List[RoomResponse])
def list_rooms(building_id: int = None, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    query = db.query(Room).options(joinedload(Room.building)).filter(Room.is_active == True)
    if building_id:
        query = query.filter(Room.building_id == building_id)
    rooms = query.order_by(Room.building_id, Room.name).all()
    return [RoomResponse(
        id=r.id,
        building_id=r.building_id,
        building_name=r.building_name or (r.building.name if r.building else None),
        name=r.name,
        floor=r.floor,
        room_type=r.room_type,
        is_active=r.is_active,
    ) for r in rooms]


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    room = Room(
        name=data.name,
        building_name=data.building_name,
        floor=data.floor,
        room_type=data.room_type,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return RoomResponse(
        id=room.id,
        building_id=room.building_id,
        building_name=room.building_name,
        name=room.name,
        floor=room.floor,
        room_type=room.room_type,
        is_active=room.is_active,
    )


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, data: RoomCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salle introuvable")
    room.name = data.name
    room.building_name = data.building_name
    room.floor = data.floor
    room.room_type = data.room_type
    db.commit()
    db.refresh(room)
    return RoomResponse(
        id=room.id,
        building_id=room.building_id,
        building_name=room.building_name,
        name=room.name,
        floor=room.floor,
        room_type=room.room_type,
        is_active=room.is_active,
    )


@router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salle introuvable")
    db.delete(room)
    db.commit()
    return {"message": "Salle supprimée"}
