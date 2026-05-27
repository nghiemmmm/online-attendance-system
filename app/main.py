from datetime import timedelta
import logging

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import exception_handler
from app.api.main import api_router
from app.core.config import settings
from app.core.security import create_access_token
from app.services.models import load_model
from app.utils.logger import logger

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

app = FastAPI(
    title=settings.APP_NAME,
    description="face recognition",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

access_token = create_access_token(
    data={"sub": "test_user"},
    expires_delta=timedelta(minutes=30000),
)
print(f"Generated test token: {access_token}")

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
exception_handler.init_app(app)

root_logger = logging.getLogger("app")
root_logger.addHandler(logging.StreamHandler())


@app.on_event("startup")
async def load():
    global model, mtcnn
    model, mtcnn = load_model()
    logger.info(f"Model and MTCNN loaded on {DEVICE}")


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
