"""Combined settings facade with domain-specific settings objects."""

from __future__ import annotations

from typing import Any

from app.core.settings_app import AppSettings
from app.core.settings_cors import CORSSettings
from app.core.settings_database import DatabaseSettings
from app.core.settings_email import EmailSettings
from app.core.settings_security import SecuritySettings


class Settings:
    def __init__(self) -> None:
        self.app = AppSettings()
        self.database = DatabaseSettings()
        self.security = SecuritySettings()
        self.email = EmailSettings()
        self.cors = CORSSettings()
        self._namespaces = (self.app, self.database, self.security, self.email, self.cors)

    def __getattr__(self, name: str) -> Any:
        for namespace in self._namespaces:
            if hasattr(namespace, name):
                return getattr(namespace, name)
        raise AttributeError(f"{type(self).__name__!s} object has no attribute {name!r}")

    def __dir__(self) -> list[str]:
        names = set(super().__dir__())
        for namespace in self._namespaces:
            names.update(dir(namespace))
        return sorted(names)


settings = Settings()
