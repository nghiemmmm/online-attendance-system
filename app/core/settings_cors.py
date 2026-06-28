"""CORS and frontend access settings."""

from __future__ import annotations

from typing import Annotated

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.settings_common import parse_cors


class CORSSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    FRONTEND_HOST: str = "http://localhost:5173"
    GOOGLE_ALLOWED_EMAIL_DOMAIN: str = ""
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]
