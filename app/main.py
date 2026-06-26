import os

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import exception_handler
from app.api.main import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.utils.logger import logger


DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

setup_logging()

# Create uploads and dataset directory if it doesn't exist
os.makedirs("uploads/faces", exist_ok=True)
os.makedirs("uploads/attendance", exist_ok=True)
os.makedirs("dataset", exist_ok=True)
os.makedirs("vector_db/embeddings_db", exist_ok=True)


app = FastAPI(
    title=settings.APP_NAME,
    description="face recognition",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(RequestLoggingMiddleware)
# Add SessionMiddleware to enable session support
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/dataset", StaticFiles(directory="dataset"), name="dataset")
exception_handler.init_app(app)


# @app.on_event("startup")
# async def load():
#     global model, mtcnn
#     model, mtcnn = load_model()
#     logger.info(f"Model and MTCNN loaded on {DEVICE}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.APP_NAME} shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
