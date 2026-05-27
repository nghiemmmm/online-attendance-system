from fastapi import APIRouter

from app.api.routes import ketnoi_router, system_router,user,login

api_router = APIRouter()
api_router.include_router(system_router.router)
api_router.include_router(ketnoi_router.router)
api_router.include_router(user.router)
api_router.include_router(login.router)