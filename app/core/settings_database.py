"""Database settings and connection URL helpers."""

from __future__ import annotations

from pydantic import PostgresDsn, computed_field

from app.core.settings_compat import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_DB: str = "diemdanh"
    DATABASE_URL: str | None = None

    def _normalize_database_url(self, url: str, async_driver: bool) -> str:
        if url.startswith("postgres://"):
            prefix = (
                "postgresql+asyncpg://" if async_driver else "postgresql+psycopg://"
            )
            url = url.replace("postgres://", prefix, 1)
        elif url.startswith("postgresql://"):
            prefix = (
                "postgresql+asyncpg://" if async_driver else "postgresql+psycopg://"
            )
            url = url.replace("postgresql://", prefix, 1)
        elif async_driver and url.startswith("postgresql+psycopg://"):
            url = url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

        if "render.com" in url and "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode=require"

        return url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn | str:
        if self.DATABASE_URL:
            return self._normalize_database_url(self.DATABASE_URL, async_driver=False)

        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_ASYNC_URI(self) -> str:
        if self.DATABASE_URL:
            return self._normalize_database_url(self.DATABASE_URL, async_driver=True)

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
