"""
Kiểm tra database trước khi backend chính thức khởi động.
Thử kết nối tới database cho tới khi DB sẵn sàng (sử dụng loop và time.sleep thay vì tenacity để giảm thư viện thừa).
"""

import logging
import time

from sqlalchemy import Engine
from sqlmodel import Session, select

from app.core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


def init(db_engine: Engine) -> None:
    tries = 0
    while tries < max_tries:
        try:
            tries += 1
            logger.info(f"Database connection attempt {tries}/{max_tries}...")
            with Session(db_engine) as session:
                # Try to create session to check if DB is awake
                session.exec(select(1))
            logger.info("Database is awake and reachable!")
            return
        except Exception as e:
            if tries >= max_tries:
                logger.error("Max database connection attempts reached. Exiting.")
                raise e
            logger.warning(f"Database not ready yet ({e}). Retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)


def main() -> None:
    logger.info("Initializing service connection checks")
    init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
