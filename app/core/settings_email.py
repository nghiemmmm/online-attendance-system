"""Email and SMTP settings."""

from __future__ import annotations

from typing_extensions import Self

from pydantic import EmailStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if self.MAIL_USERNAME and not self.SMTP_USER:
            self.SMTP_USER = self.MAIL_USERNAME
        if self.MAIL_PASSWORD and not self.SMTP_PASSWORD:
            self.SMTP_PASSWORD = self.MAIL_PASSWORD
        if self.SMTP_USER and not self.SMTP_HOST:
            self.SMTP_HOST = "smtp.gmail.com"
        if self.SMTP_USER and not self.EMAILS_FROM_EMAIL:
            self.EMAILS_FROM_EMAIL = self.SMTP_USER
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = "Hệ Thống Điểm Danh"
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)
