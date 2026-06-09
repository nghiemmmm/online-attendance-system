import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging_config import set_request_id

REQUEST_ID_HEADER = "X-Request-ID"

logger = logging.getLogger("app.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request/response cơ bản, không ghi body hay thông tin nhạy cảm."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
        set_request_id(request_id)
        started_at = time.perf_counter()
        client_ip = request.client.host if request.client else "-"
        user_agent = request.headers.get("user-agent", "-")

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - started_at) * 1000
            logger.exception(
                "request_failed method=%s path=%s duration_ms=%.2f ip=%s user_agent=%s",
                request.method,
                request.url.path,
                duration_ms,
                client_ip,
                user_agent,
            )
            raise

        duration_ms = (time.perf_counter() - started_at) * 1000
        response.headers[REQUEST_ID_HEADER] = request_id
        logger.info(
            "request_completed method=%s path=%s status_code=%s duration_ms=%.2f ip=%s user_agent=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_ip,
            user_agent,
        )
        return response
