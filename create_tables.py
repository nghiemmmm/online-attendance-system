from sqlalchemy import create_engine
from sqlmodel import SQLModel

engine = create_engine(
    "postgresql+psycopg://postgres:postgres@localhost:5432/attendance_db"
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")


if __name__ == "__main__":
    create_db_and_tables()
