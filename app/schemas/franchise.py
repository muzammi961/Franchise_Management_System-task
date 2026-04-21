from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class FranchiseCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    address: str
    franchise_code: str


class FranchiseUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None


class FranchiseResponse(BaseModel):
    id: int
    user_id: int
    name: str
    phone: str
    address: str
    franchise_code: str
    created_at: datetime
    email: Optional[str] = None

    class Config:
        from_attributes = True


class FranchiseListResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: list[FranchiseResponse]
