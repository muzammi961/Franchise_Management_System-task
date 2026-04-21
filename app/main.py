from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.database import create_tables
from app.middleware.auth_middleware import AuthMiddleware
from app.routes import auth, franchise, profile, websocket
from app.utils.redis import close_redis


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="FastAPI JWT Authentication with Super Admin & Franchise Management System",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(AuthMiddleware)

    application.include_router(auth.router)
    application.include_router(franchise.router)
    application.include_router(profile.router)
    application.include_router(websocket.router)

    return application


app = create_application()


@app.on_event("startup")
async def on_startup():
    create_tables()


@app.on_event("shutdown")
async def on_shutdown():
    await close_redis()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "data": None,
            "error": str(exc),
        },
    )

@app.get("/health", tags=["Health"])
async def health_check():
    return {"success": True, "message": "Service is running", "data": {"version": settings.APP_VERSION}, "error": None}
