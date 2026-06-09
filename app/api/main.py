from fastapi import APIRouter

from app.api.routes import google_auth_router, ketnoi_router, login, system_router, user

api_router = APIRouter()
api_router.include_router(system_router.router)
api_router.include_router(ketnoi_router.router)
api_router.include_router(google_auth_router.router)
api_router.include_router(user.router)
api_router.include_router(login.router)
