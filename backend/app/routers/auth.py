from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, PasswordChangeRequest, StudentRegisterRequest
from app.services.auth_service import authenticate_user, create_access_token, hash_password, verify_password
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentification"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == req.login) | (User.username == req.login)
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiant ou mot de passe incorrect")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Votre compte n'a pas encore été activé par un administrateur")
    user = authenticate_user(db, user, req.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiant ou mot de passe incorrect")
    access_token = create_access_token(data={"user_id": user.id, "role_id": user.role_id, "role": user.role.name})
    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        role=user.role.name,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email or "",
        username=user.username,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: StudentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == req.username) | ((User.email == req.email) if req.email else False)
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce nom d'utilisateur ou email existe déjà")

    user = User(
        role_id=3,
        username=req.username,
        first_name=req.first_name,
        last_name=req.last_name,
        genre=req.genre.upper(),
        niveau_etude=req.niveau_etude,
        programme=req.programme,
        email=req.email,
        password_hash=hash_password(req.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    return {"message": "Inscription réussie. Vous pouvez maintenant vous connecter."}


@router.post("/change-password")
def change_password(req: PasswordChangeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ancien mot de passe incorrect")
    current_user.password_hash = hash_password(req.new_password)
    current_user.password_changed_at = None
    db.commit()
    return {"message": "Mot de passe modifie avec succes"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "role": current_user.role.name,
        "role_id": current_user.role_id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "username": current_user.username,
        "genre": current_user.genre,
        "niveau_etude": current_user.niveau_etude,
        "programme": current_user.programme,
        "student_id": current_user.student_id,
        "is_active": current_user.is_active,
    }
