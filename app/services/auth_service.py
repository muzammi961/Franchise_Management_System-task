import json
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.franchise import Franchise
from app.core.security import verify_password, hash_password
from app.utils.jwt import create_token_pair, decode_token, TOKEN_TYPE_REFRESH
from app.utils.redis import redis_set, redis_get, redis_exists, redis_delete
from app.core.config import settings


BLACKLIST_PREFIX = "blacklist:"
PROFILE_PREFIX = "profile:"
PROFILE_CACHE_TTL = 300  


async def authenticate_user(
    db: Session,
    email: str,
    password: str,
    franchise_code: Optional[str],
) -> dict:
    user: Optional[User] = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if user.role == UserRole.FRANCHISE:
        if not franchise_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="franchise_code is required for franchise login",
            )
        franchise: Optional[Franchise] = db.query(Franchise).filter(
            Franchise.user_id == user.id,
            Franchise.franchise_code == franchise_code,
        ).first()
        if not franchise:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid franchise_code",
            )

    access_token, refresh_token = create_token_pair(user.id, user.email, user.role.value)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role.value,
    }


async def refresh_access_token(db: Session, refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if payload.get("type") != TOKEN_TYPE_REFRESH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not a refresh token",
        )

    jti = payload.get("jti")
    if jti and await redis_exists(f"{BLACKLIST_PREFIX}{jti}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    user_id = int(payload["sub"])
    email = payload["email"]
    role = payload["role"]

    user: Optional[User] = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
        )

    from datetime import datetime, timezone
    exp = payload.get("exp")
    if exp:
        ttl = int(exp - datetime.now(timezone.utc).timestamp())
        if ttl > 0:
            await redis_set(f"{BLACKLIST_PREFIX}{jti}", "1", ttl)

    access_token, new_refresh_token = create_token_pair(user_id, email, role)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "role": role,
    }


async def logout_user(jti: str, exp: int) -> None:
    from datetime import datetime, timezone
    ttl = int(exp - datetime.now(timezone.utc).timestamp())
    if ttl > 0:
        await redis_set(f"{BLACKLIST_PREFIX}{jti}", "1", ttl)


async def get_cached_profile(user_id: int) -> Optional[dict]:
    raw = await redis_get(f"{PROFILE_PREFIX}{user_id}")
    if raw:
        return json.loads(raw)
    return None


async def set_cached_profile(user_id: int, profile_data: dict) -> None:
    await redis_set(f"{PROFILE_PREFIX}{user_id}", json.dumps(profile_data), PROFILE_CACHE_TTL)


async def invalidate_profile_cache(user_id: int) -> None:
    await redis_delete(f"{PROFILE_PREFIX}{user_id}")
