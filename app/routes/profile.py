import json
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.franchise import Franchise
from app.schemas.user import ProfileUpdateRequest
from app.core.security import hash_password
from app.dependencies.role_checker import require_any_role
from app.services.auth_service import get_cached_profile, set_cached_profile, invalidate_profile_cache

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


def success_response(message: str, data=None):
    return {"success": True, "message": message, "data": data, "error": None}


@router.get("", response_model=None)
async def get_profile(db: Session = Depends(get_db),current_user: dict = Depends(require_any_role),):
    user_id = current_user["user_id"]

    cached = await get_cached_profile(user_id)
    if cached:
        return success_response("Profile retrieved successfully", cached)

    user: User = db.query(User).filter(User.id == user_id).first()

    profile_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),}

    if user.role == UserRole.FRANCHISE and user.franchise:
        profile_data["franchise"] = {
            "id": user.franchise.id,
            "name": user.franchise.name,
            "phone": user.franchise.phone,
            "address": user.franchise.address,
            "franchise_code": user.franchise.franchise_code,
        }

    await set_cached_profile(user_id, profile_data)
    return success_response("Profile retrieved successfully", profile_data)


@router.put("", response_model=None)
async def update_profile(
    body: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_role),
):
    user_id = current_user["user_id"]
    user: User = db.query(User).filter(User.id == user_id).first()

    if body.password is not None:
        user.password = hash_password(body.password)

    if user.role == UserRole.FRANCHISE and user.franchise:
        franchise: Franchise = user.franchise
        if body.name is not None:
            franchise.name = body.name
        if body.phone is not None:
            franchise.phone = body.phone
        if body.address is not None:
            franchise.address = body.address

    db.commit()
    db.refresh(user)

    await invalidate_profile_cache(user_id)

    profile_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }

    if user.role == UserRole.FRANCHISE and user.franchise:
        profile_data["franchise"] = {
            "id": user.franchise.id,
            "name": user.franchise.name,
            "phone": user.franchise.phone,
            "address": user.franchise.address,
            "franchise_code": user.franchise.franchise_code,
        }

    return success_response("Profile updated successfully", profile_data)
