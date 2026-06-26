import logging
from dataclasses import dataclass
from typing import Mapping

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException

DEFAULT_DEVELOPER_MESSAGE = ""
DEFAULT_CODE = "000"

logger = logging.getLogger(__name__)


def init_app(app: FastAPI) -> None:
    # 例外ハンドラの登録
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(404, not_found_handler)
    app.add_exception_handler(AppException, app_exception_handler)


@dataclass(frozen=True)
class Error:
    developer_message: str = ""
    code: str = "000"

    def to_response(self) -> Mapping:
        return {
            "code": self.code,
            "developer_message": self.developer_message,
        }


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:

    logger.warning("request_validation_error path=%s error=%s", request.url.path, exc)
    errors = [Error(developer_message=str(exc))]
    return JSONResponse(
        status_code=400, content={"errors": [error.to_response() for error in errors]}
    )


async def not_found_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """404のエラーハンドラー"""
    logger.info("not_found path=%s", request.url.path)
    error = Error(
        developer_message="Not found",
        code=DEFAULT_CODE,
    )
    return JSONResponse(status_code=404, content={"errors": [error.to_response()]})


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.error("app_exception path=%s detail=%s status_code=%s", request.url.path, exc.detail, exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
