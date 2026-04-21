from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.franchise import FranchiseCreateRequest, FranchiseUpdateRequest
from app.services import franchise_service
from app.dependencies.role_checker import require_super_admin, require_any_role

router = APIRouter(prefix="/api/v1/franchise", tags=["Franchise"])


def success_response(message: str, data=None):
    return {"success": True, "message": message, "data": data, "error": None}


@router.post("", response_model=None)
async def create_franchise(
    body: FranchiseCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    franchise = await franchise_service.create_franchise(db=db, data=body)
    return success_response("Franchise created successfully", franchise.model_dump())


@router.get("", response_model=None)
async def list_franchises(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    result = await franchise_service.get_all_franchises(db=db, page=page, limit=limit, search=search)
    result["items"] = [item.model_dump() for item in result["items"]]
    return success_response("Franchises retrieved successfully", result)


@router.get("/{franchise_id}", response_model=None)
async def get_franchise(
    franchise_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_any_role),
):
    franchise = await franchise_service.get_franchise_by_id(db=db, franchise_id=franchise_id)
    return success_response("Franchise retrieved successfully", franchise.model_dump())


@router.put("/{franchise_id}", response_model=None)
async def update_franchise(
    franchise_id: int,
    body: FranchiseUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    franchise = await franchise_service.update_franchise(db=db, franchise_id=franchise_id, data=body)
    return success_response("Franchise updated successfully", franchise.model_dump())


@router.delete("/{franchise_id}", response_model=None)
async def delete_franchise(
    franchise_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_super_admin),
):
    await franchise_service.delete_franchise(db=db, franchise_id=franchise_id)
    return success_response("Franchise deleted successfully")
