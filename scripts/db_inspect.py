import asyncio
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.settings_database import DatabaseSettings


def _safe_str(v: object) -> str:
    if isinstance(v, (datetime,)):
        return v.isoformat()
    return str(v)


async def fetch_all(engine, query: str, params: dict | None = None, limit: int = 200):
    async with engine.connect() as conn:
        res = await conn.execute(text(query), params or {})
        rows = res.fetchall()
        return rows[:limit], res.keys()


async def main():
    ds = DatabaseSettings()
    engine = create_async_engine(ds.SQLALCHEMY_DATABASE_ASYNC_URI, pool_pre_ping=True)

    print("DB_URI_ASYNC=", ds.SQLALCHEMY_DATABASE_ASYNC_URI)

    # List tables
    tables_q = """
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_type='BASE TABLE'
      AND table_schema NOT IN ('pg_catalog','information_schema')
    ORDER BY 1,2;
    """
    rows, keys = await fetch_all(engine, tables_q, limit=500)
    print("\nTABLES_COUNT=", len(rows))
    for r in rows:
        print(f"{r[0]}.{r[1]}")

    # Try to fetch sample data from a few expected tables (if they exist)
    candidate_tables = [
        "taikhoan",
        "sinhvien",
        "canbo",
        "lophocphan",
        "buoihoc",
        "diemdanh",
        "khieunai",
    ]

    async with engine.connect() as conn:
        for t in candidate_tables:
            # discover columns
            cols_q = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public'
              AND table_name=:t
            ORDER BY ordinal_position;
            """
            cols = await conn.execute(text(cols_q), {"t": t})
            col_rows = cols.fetchall()
            if not col_rows:
                continue

            col_names = [c[0] for c in col_rows]
            # pick up to first 6 columns for display
            show_cols = col_names[:6]
            select_q = (
                f"SELECT {', '.join(show_cols)} FROM public.{t} "
                "LIMIT 5;"
            )
            data_res = await conn.execute(text(select_q))
            data_rows = data_res.fetchall()
            data_keys = data_res.keys()

            print(f"\nSAMPLE public.{t} (showing columns: {show_cols})")
            for dr in data_rows:
                line = ", ".join(f"{k}={_safe_str(v)}" for k, v in zip(data_keys, dr))
                print(line)


if __name__ == "__main__":
    asyncio.run(main())

