"""Compatibility facade for application settings.

Keep importing `settings` from this module to avoid changing the rest of the codebase.
The actual settings are split by domain in `app.core.settings_*` modules.
"""

from app.core.settings import Settings, settings

