from sqlalchemy import text

from app.core.db import engine

with engine.begin() as conn:
    with open("init.sql", encoding="utf-8") as f:
        sql = f.read()
    conn.execute(text(sql))
    print("DB Initialized Correctly")
