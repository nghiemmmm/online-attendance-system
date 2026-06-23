
from app.core.db import engine
from sqlalchemy import text

with engine.begin() as conn:
    with open('init.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.execute(text(sql))
    print('DB Initialized Correctly')

