"""Compatibility helpers for application settings imports.

When `pydantic-settings` is unavailable in the runtime used by pytest, we still
need settings objects to import cleanly. The fallback base class below reads
matching environment variables into Pydantic models.
"""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover - fallback for stripped runtimes

    class BaseSettings(BaseModel):
        """Fallback replacement that populates fields from environment variables."""

        def __init__(self, **data: Any) -> None:
            for field_name in self.model_fields:
                env_value = os.getenv(field_name)
                if env_value is not None and field_name not in data:
                    data[field_name] = env_value
            super().__init__(**data)

    def SettingsConfigDict(**kwargs: Any) -> dict[str, Any]:
        return kwargs
