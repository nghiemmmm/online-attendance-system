from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import Account, AccountCreate


def _build_async_session_factory():
    """Create the async session factory when the configured DB URL supports it."""
    async_database_url = str(settings.SQLALCHEMY_DATABASE_ASYNC_URI)
    database_url = make_url(async_database_url)

    if database_url.drivername == "sqlite" and "+aiosqlite" not in async_database_url:
        return None

    async_engine = create_async_engine(
        async_database_url,
        pool_pre_ping=True,
        echo=False,  # Set to True for SQL debugging
        future=True,  # Use SQLAlchemy 2.0 style
    )

    return async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


# ✅ ASYNC sessionmaker (disabled for plain SQLite test databases)
AsyncSessionFactory = _build_async_session_factory()

# ⚠️ SYNC engine (temporary, for backward compatibility with existing sync routes)
# This should be removed once all routes are migrated to async
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


async def ensure_pgvector_extension(session: AsyncSession) -> None:
    """Enable pgvector extension for vector similarity search."""
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    await session.commit()


async def init_db_async(session: AsyncSession) -> None:
    """Initialize database with default superuser (async version)."""
    # await ensure_pgvector_extension(session)

    stmt = select(Account).where(Account.username == settings.FIRST_SUPERUSER)
    result = await session.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
        account_in = AccountCreate(
            username=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            role="ADMIN",
        )
        # TODO: Implement async version of create_account
        # For now, creating directly with ORM
        from app.core.security import get_password_hash

        account = Account(
            username=account_in.username,
            password_hash=get_password_hash(account_in.password),
            role=account_in.role,
        )
        session.add(account)
        await session.commit()
        await session.refresh(account)


# ⚠️ DEPRECATED: Keep for backward compatibility only
def ensure_pgvector_extension_sync(session) -> None:
    """DEPRECATED: Use ensure_pgvector_extension instead."""
    session.exec(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    session.commit()


def init_db_sync(session) -> None:
    """DEPRECATED: Use init_db_async instead."""
    from sqlmodel import create_engine as sqlmodel_create_engine

    sync_engine = sqlmodel_create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    with Session(sync_engine) as sync_session:
        stmt = select(Account).where(Account.username == settings.FIRST_SUPERUSER)
        account = sync_session.exec(stmt).first()
        if not account:
            account_in = AccountCreate(
                username=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                role="ADMIN",
            )
            crud.create_account(session=sync_session, account_create=account_in)


def init_db(session) -> None:
    """Initialize database using the synchronous bootstrap path."""
    init_db_sync(session)
