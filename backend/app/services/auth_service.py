from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.models.system_config import SystemConfig

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_config_int(db: Session, key: str, default: int) -> int:
    config = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if config and config.config_value:
        try:
            return int(config.config_value)
        except ValueError:
            return default
    return default


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, user: User, password: str) -> Optional[User]:
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        return None
    if not verify_password(password, user.password_hash):
        user.failed_login_attempts += 1
        max_attempts = get_config_int(db, "max_login_attempts", 5)
        if user.failed_login_attempts >= max_attempts:
            lock_minutes = get_config_int(db, "lockout_minutes", 30)
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lock_minutes)
        db.commit()
        return None
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return user
