from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    first_name: str
    last_name: str
    email: str = ""
    username: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class StudentRegisterRequest(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    genre: str
    niveau_etude: str
    programme: str
    email: Optional[str] = None
