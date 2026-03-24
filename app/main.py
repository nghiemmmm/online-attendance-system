from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.core.config import settings
# from app.api.routes import detection, health
from app.utils.logger import logger

from datetime import timedelta
from app.core.security import create_access_token

import asyncio
import logging
import secrets
import uuid
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRelay
from app.frontend.my_media_transform_check import VideoTransformTrack
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app import exception_handler
from app.api.routes import ketnoi_router
# Create FastAPI application
app = FastAPI(
    # title=settings.APP_NAME,
    description="face recognition",
    # version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

access_token = create_access_token(
    data={"sub": "test_user"}, 
    expires_delta=timedelta(minutes=30000)
)
print(f"Generated test token: {access_token}")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
exception_handler.init_app(app)
root_logger = logging.getLogger("app")
root_logger.addHandler(logging.StreamHandler())

pcs = set()
dcs = set()
relay = MediaRelay()

@app.get("/", include_in_schema=False)
async def index(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", include_in_schema=False)
def health() -> JSONResponse:
    """ヘルスチェック"""
    return JSONResponse({"message": "It worked!!"})


app.include_router(ketnoi_router.router)

@app.post("/message", include_in_schema=False)
async def message(request: Request):
    params = await request.json()
    [dc.send(params["message"]) for dc in dcs]



@app.get("/home/")
def home():
    return {"message": "Welcome"}

@app.get("/")
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/api/docs")

@app.get("/ui-redirect")
async def ui_redirect():
    """Redirect to Gradio UI"""
    return RedirectResponse(url="/ui")

@app.on_event("startup")
async def startup_event():
    """Application startup events"""
    logger.info(f"{settings.APP_NAME} v{settings.VERSION} starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown events"""
    logger.info(f"{settings.APP_NAME} v{settings.VERSION} shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )