from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, RefreshTokenRequest, SendOTPRequest, VerifyOTPRequest
from app.services import auth_service, otp_service
from app.dependencies.role_checker import require_any_role

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def success_response(message: str, data: dict = None):
    return {"success": True, "message": message, "data": data, "error": None}


@router.post("/login", response_model=None)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    result = await auth_service.authenticate_user(
        db=db,
        email=body.email,
        password=body.password,
        franchise_code=body.franchise_code,
    )
    return success_response("Login successful", result)


@router.post("/refresh-token", response_model=None)
async def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    result = await auth_service.refresh_access_token(db=db, refresh_token=body.refresh_token)
    return success_response("Token refreshed successfully", result)


@router.post("/logout", response_model=None)
async def logout(request: Request, current_user: dict = Depends(require_any_role)):
    await auth_service.logout_user(
        jti=current_user["jti"],
        exp=current_user["exp"],
    )
    return success_response("Logged out successfully")


@router.post("/send-otp", response_model=None)
async def send_otp(body: SendOTPRequest):
    await otp_service.send_otp(email=body.email)
    return success_response("OTP sent successfully. Check your email.")


@router.post("/verify-otp", response_model=None)
async def verify_otp(body: VerifyOTPRequest):
    await otp_service.verify_otp(email=body.email, otp=body.otp)
    return success_response("OTP verified successfully")
