import sqlalchemy
from sqlmodel import SQLModel
from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg://postgres:postgres@localhost:5432/attendance_db')

from app import models

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_db_and_tables()
