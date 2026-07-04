import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import exception_handler
from app.api.main import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.services.face_service import get_or_create_face_service
from app.utils.logger import logger


setup_logging()

# Create uploads, dataset and static directory if it doesn't exist
os.makedirs("app/static", exist_ok=True)
os.makedirs("uploads/faces", exist_ok=True)
os.makedirs("uploads/attendance", exist_ok=True)
os.makedirs("dataset", exist_ok=True)
os.makedirs("vector_db/embeddings_db", exist_ok=True)
# tesssssss

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis connection pool
    from app.core.redis import init_redis_client
    await init_redis_client()

    app.state.face_service = get_or_create_face_service()
    logger.info("FaceRecognitionService initialized and cached in app.state")
    
    # Spawn daily background cleanup task (deletes attendance images older than 1 day)
    import asyncio
    async def periodic_cleanup():
        from app.services.cleanup_service import cleanup_expired_attendance_evidence
        logger.info("Starting periodic attendance evidence cleanup task...")
        while True:
            try:
                deleted = cleanup_expired_attendance_evidence(days=1)
                if deleted > 0:
                    logger.info(f"Periodic Cleanup: Successfully removed {deleted} expired attendance images.")
            except Exception as e:
                logger.error(f"Error in periodic cleanup background task: {e}")
            await asyncio.sleep(24 * 3600)

    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # Clean up background task, active WebRTC peer connections, and Redis client
    cleanup_task.cancel()
    try:
        from app.services.webrtc_manager import get_webrtc_manager
        webrtc_manager = get_webrtc_manager()
        await webrtc_manager.close_all()
        logger.info("Closed all active WebRTC connections on shutdown.")
    except Exception as e:
        logger.error(f"Error closing WebRTC connections on shutdown: {e}")
        
    try:
        from app.core.redis import close_redis_client
        await close_redis_client()
    except Exception as e:
        logger.error(f"Error closing Redis connection on shutdown: {e}")
        
    logger.info("%s shutting down...", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description="face recognition",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
# Add SessionMiddleware to enable session support
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/dataset", StaticFiles(directory="dataset"), name="dataset")
exception_handler.init_app(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
