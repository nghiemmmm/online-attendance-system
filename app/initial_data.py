'''
là file seed dữ liệu ban đầu cho backend. Nó không chạy API, mà chỉ được gọi lúc khởi động để kiểm tra và tạo dữ liệu tối thiểu cần có.

Nó làm 3 việc:

Mở Session với engine từ db.py:1.
Gọi init_db(session) để khởi tạo dữ liệu.
Log ra “Creating initial data” và “Initial data created”.
'''
import logging

from sqlmodel import Session

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
