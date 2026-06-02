from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TicketCreate(BaseModel):
    category_id: int
    subcategory_id: Optional[int] = None
    room_id: int
    workstation_number: Optional[str] = None
    description: Optional[str] = None
    priority: str = "medium"


class TicketStatusUpdate(BaseModel):
    status_id: int
    comment: Optional[str] = None
    resolution_notes: Optional[str] = None


class TicketAssign(BaseModel):
    technician_id: int


class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    user_id: int
    user_name: str
    category_id: int
    category_name: str
    subcategory_id: Optional[int] = None
    subcategory_name: Optional[str] = None
    room_id: int
    room_name: str
    building_name: str
    workstation_number: Optional[str] = None
    description: Optional[str] = None
    status_id: int
    status_label: str
    assigned_to: Optional[int] = None
    technician_name: Optional[str] = None
    priority: str
    source: str
    sla_deadline: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    total: int
    tickets: List[TicketResponse]


class MessageSend(BaseModel):
    message: str
    message_type: str = "text"
    attachment_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    sender_name: str
    message: str
    message_type: str = "text"
    is_deleted: bool = False
    attachment_id: Optional[int] = None
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None
    attachment_type: Optional[str] = None
    public_url: Optional[str] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationCreate(BaseModel):
    rating: int
    comment: Optional[str] = None


class EvaluationResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
