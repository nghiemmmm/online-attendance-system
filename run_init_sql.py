import sqlalchemy
from sqlalchemy import text, create_engine

# URL from init.sql / environment or fixed for local
engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/attendance_db")

with engine.connect() as conn:
    sql = open('init.sql', encoding='utf-8').read()
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        if not stmt.startswith('--') and not stmt.startswith('/*'):
            conn.execute(text(stmt))
    conn.commit()
    print('DB Initialized')
