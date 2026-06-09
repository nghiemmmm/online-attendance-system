import logging
import sys
from contextvars import ContextVar

from app.core.config import settings


request_id_context: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Gắn request_id hiện tại vào mỗi log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


def set_request_id(request_id: str) -> None:
    """Lưu request_id của request hiện tại vào context logging."""
    request_id_context.set(request_id)


def get_request_id() -> str:
    """Lấy request_id hiện tại để log hoặc trả về response."""
    return request_id_context.get()


def setup_logging() -> None:
    """Cấu hình logging trung tâm cho backend và tránh gắn handler trùng lặp."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | request_id=%(request_id)s | %(message)s"
    )
    request_id_filter = RequestIdFilter()

    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    app_logger.propagate = False

    if not app_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        handler.addFilter(request_id_filter)
        app_logger.addHandler(handler)
    else:
        for handler in app_logger.handlers:
            handler.setLevel(log_level)
            handler.setFormatter(formatter)
            if not any(isinstance(f, RequestIdFilter) for f in handler.filters):
                handler.addFilter(request_id_filter)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.setLevel(log_level)
        for handler in uvicorn_logger.handlers:
            if not any(isinstance(f, RequestIdFilter) for f in handler.filters):
                handler.addFilter(request_id_filter)
