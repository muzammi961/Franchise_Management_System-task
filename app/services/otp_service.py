from fastapi import HTTPException, status
from app.utils.otp import generate_otp
from app.utils.smtp import send_otp_email
from app.utils.redis import redis_set, redis_get, redis_delete, redis_incr, redis_expire, redis_exists
from app.core.config import settings

OTP_PREFIX = "otp:"
OTP_LIMIT_PREFIX = "otp_limit:"


async def send_otp(email: str) -> None:
    limit_key = f"{OTP_LIMIT_PREFIX}{email}"

    count_raw = await redis_get(limit_key)
    count = int(count_raw) if count_raw else 0

    if count >= settings.OTP_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Max {settings.OTP_MAX_REQUESTS} OTP requests allowed per {settings.OTP_RATE_LIMIT_MINUTES} minutes",
        )

    otp = generate_otp()
    ttl_seconds = settings.OTP_EXPIRE_MINUTES * 60
    await redis_set(f"{OTP_PREFIX}{email}", otp, ttl_seconds)

    new_count = await redis_incr(limit_key)
    if new_count == 1:
        rate_ttl = settings.OTP_RATE_LIMIT_MINUTES * 60
        await redis_expire(limit_key, rate_ttl)

    await send_otp_email(email, otp)


async def verify_otp(email: str, otp: str) -> bool:
    otp_key = f"{OTP_PREFIX}{email}"
    stored_otp = await redis_get(otp_key)

    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired or not found. Please request a new one.",
        )

    if stored_otp != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP",
        )
    await redis_delete(otp_key)
    return True
