import sqlalchemy
from sqlalchemy import text, create_engine

engine = create_engine('postgresql+psycopg://postgres:postgres@localhost:5432/postgres')
with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    conn.execute(text("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'attendance_db' AND pid != pg_backend_pid();"))
    print('Terminated other connections')
