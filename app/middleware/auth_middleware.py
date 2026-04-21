from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.jwt import decode_token, TOKEN_TYPE_ACCESS
from app.utils.redis import redis_exists

BLACKLIST_PREFIX = "blacklist:"

PUBLIC_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/refresh-token",
    "/api/v1/auth/send-otp",
    "/api/v1/auth/verify-otp",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/ws/notifications",
}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in PUBLIC_PATHS or path.startswith("/ws/"):
            return await call_next(request)

        authorization: str = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Missing or invalid Authorization header", "data": None, "error": "UNAUTHORIZED"},)

        token = authorization.split(" ", 1)[1]

        try:
            payload = decode_token(token)
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Invalid or expired token", "data": None, "error": "INVALID_TOKEN"},
            )

        if payload.get("type") != TOKEN_TYPE_ACCESS:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,content={"success": False, "message": "Token is not an access token", "data": None, "error": "WRONG_TOKEN_TYPE"},)

        jti = payload.get("jti")
        if jti and await redis_exists(f"{BLACKLIST_PREFIX}{jti}"):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,content={"success": False, "message": "Token has been revoked", "data": None, "error": "TOKEN_REVOKED"},)

        request.state.user_id = int(payload["sub"])
        request.state.email = payload["email"]
        request.state.role = payload["role"]
        request.state.jti = jti
        request.state.exp = payload.get("exp")

        return await call_next(request)
