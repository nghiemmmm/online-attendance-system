from fastapi import APIRouter

from app.api.routes import (
    canbo,
    canhbaohoc_tap,
    diemdanh,
    google_auth_router,
    khieunai,
    ketnoi_router,
    lichhoc,
    login,
    sinhvien,
    system_router,
    user,
)

api_router = APIRouter()
api_router.include_router(system_router.router)
api_router.include_router(ketnoi_router.router)
api_router.include_router(google_auth_router.router)
api_router.include_router(user.router)
api_router.include_router(login.router)
api_router.include_router(canbo.router)
api_router.include_router(canhbaohoc_tap.router)
api_router.include_router(diemdanh.router)
api_router.include_router(khieunai.router)
api_router.include_router(sinhvien.router)
api_router.include_router(lichhoc.router)
