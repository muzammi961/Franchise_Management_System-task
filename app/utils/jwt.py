from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import uuid
from jose import JWTError, jwt
from app.core.config import settings

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def _build_payload(user_id: int, email: str, role: str, token_type: str, expires_delta: timedelta) -> dict:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    jti = str(uuid.uuid4())
    return {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": token_type,
        "exp": expire,
        "iat": now,
        "jti": jti,
    }


def create_access_token(user_id: int, email: str, role: str) -> str:
    payload = _build_payload(
        user_id=user_id,
        email=email,
        role=role,
        token_type=TOKEN_TYPE_ACCESS,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int, email: str, role: str) -> str:
    payload = _build_payload(
        user_id=user_id,
        email=email,
        role=role,
        token_type=TOKEN_TYPE_REFRESH,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc


def create_token_pair(user_id: int, email: str, role: str) -> Tuple[str, str]:
    access_token = create_access_token(user_id, email, role)
    refresh_token = create_refresh_token(user_id, email, role)
    return access_token, refresh_token
