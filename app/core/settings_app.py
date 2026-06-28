"""Application-level settings."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import AnyUrl, BeforeValidator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.settings_common import parse_cors, parse_debug


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_NAME: str = "attendance"
    PROJECT_NAME: str = "attendance"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 5050
    ENVIRONMENT: str = "local"
    DEBUG: Annotated[bool, BeforeValidator(parse_debug)] = False

    FRONTEND_HOST: str = "http://localhost:5173"
    GOOGLE_ALLOWED_EMAIL_DOMAIN: str = ""
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]
