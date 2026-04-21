import json
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.franchise import Franchise
from app.schemas.franchise import FranchiseCreateRequest, FranchiseUpdateRequest, FranchiseResponse
from app.core.security import hash_password
from app.utils.redis import redis_set, redis_get, redis_delete

FRANCHISE_CACHE_PREFIX = "franchise:"
FRANCHISE_CACHE_TTL = 300


def _franchise_to_dict(franchise: Franchise, email: str) -> dict:
    return {
        "id": franchise.id,
        "user_id": franchise.user_id,
        "name": franchise.name,
        "phone": franchise.phone,
        "address": franchise.address,
        "franchise_code": franchise.franchise_code,
        "created_at": franchise.created_at.isoformat(),
        "email": email,
    }


async def create_franchise(db: Session, data: FranchiseCreateRequest) -> FranchiseResponse:
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_code = db.query(Franchise).filter(Franchise.franchise_code == data.franchise_code).first()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="franchise_code already exists",
        )

    user = User(
        email=data.email,
        password=hash_password(data.password),
        role=UserRole.FRANCHISE,
        is_active=True,
    )
    db.add(user)
    db.flush()

    franchise = Franchise(
        user_id=user.id,
        name=data.name,
        phone=data.phone,
        address=data.address,
        franchise_code=data.franchise_code,
    )
    db.add(franchise)
    db.commit()
    db.refresh(franchise)

    await redis_set(
        f"{FRANCHISE_CACHE_PREFIX}{franchise.id}",
        json.dumps(_franchise_to_dict(franchise, data.email)),
        FRANCHISE_CACHE_TTL,
    )

    return FranchiseResponse(
        id=franchise.id,
        user_id=franchise.user_id,
        name=franchise.name,
        phone=franchise.phone,
        address=franchise.address,
        franchise_code=franchise.franchise_code,
        created_at=franchise.created_at,
        email=data.email,
    )


async def get_all_franchises(
    db: Session,
    page: int,
    limit: int,
    search: Optional[str],
) -> dict:
    query = db.query(Franchise, User).join(User, Franchise.user_id == User.id)

    if search:
        like = f"%{search}%"
        query = query.filter(
            (Franchise.name.ilike(like))
            | (User.email.ilike(like))
            | (Franchise.phone.ilike(like))
            | (Franchise.franchise_code.ilike(like))
        )

    total = query.count()
    rows = query.offset((page - 1) * limit).limit(limit).all()

    items = [
        FranchiseResponse(
            id=f.id,
            user_id=f.user_id,
            name=f.name,
            phone=f.phone,
            address=f.address,
            franchise_code=f.franchise_code,
            created_at=f.created_at,
            email=u.email,
        )
        for f, u in rows
    ]

    return {"total": total, "page": page, "limit": limit, "items": items}


async def get_franchise_by_id(db: Session, franchise_id: int) -> FranchiseResponse:
    cached = await redis_get(f"{FRANCHISE_CACHE_PREFIX}{franchise_id}")
    if cached:
        data = json.loads(cached)
        from datetime import datetime
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return FranchiseResponse(**data)

    row = (
        db.query(Franchise, User)
        .join(User, Franchise.user_id == User.id)
        .filter(Franchise.id == franchise_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Franchise not found")

    franchise, user = row
    await redis_set(
        f"{FRANCHISE_CACHE_PREFIX}{franchise_id}",
        json.dumps(_franchise_to_dict(franchise, user.email)),
        FRANCHISE_CACHE_TTL,
    )

    return FranchiseResponse(
        id=franchise.id,
        user_id=franchise.user_id,
        name=franchise.name,
        phone=franchise.phone,
        address=franchise.address,
        franchise_code=franchise.franchise_code,
        created_at=franchise.created_at,
        email=user.email,
    )


async def update_franchise(db: Session, franchise_id: int, data: FranchiseUpdateRequest) -> FranchiseResponse:
    row = (
        db.query(Franchise, User)
        .join(User, Franchise.user_id == User.id)
        .filter(Franchise.id == franchise_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Franchise not found")

    franchise, user = row

    if data.name is not None:
        franchise.name = data.name
    if data.phone is not None:
        franchise.phone = data.phone
    if data.address is not None:
        franchise.address = data.address
    if data.password is not None:
        user.password = hash_password(data.password)

    db.commit()
    db.refresh(franchise)

    await redis_delete(f"{FRANCHISE_CACHE_PREFIX}{franchise_id}")

    return FranchiseResponse(
        id=franchise.id,
        user_id=franchise.user_id,
        name=franchise.name,
        phone=franchise.phone,
        address=franchise.address,
        franchise_code=franchise.franchise_code,
        created_at=franchise.created_at,
        email=user.email,
    )


async def delete_franchise(db: Session, franchise_id: int) -> None:
    row = (
        db.query(Franchise, User)
        .join(User, Franchise.user_id == User.id)
        .filter(Franchise.id == franchise_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Franchise not found")

    franchise, user = row
    db.delete(franchise)
    db.delete(user)
    db.commit()
    await redis_delete(f"{FRANCHISE_CACHE_PREFIX}{franchise_id}")
