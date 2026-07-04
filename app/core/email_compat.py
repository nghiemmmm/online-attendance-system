"""Compatibility alias for email-typed fields.

Some test environments do not have the optional `email-validator` dependency
installed, which makes Pydantic's `EmailStr` unusable at import time. This
module keeps imports working by falling back to `str`.
"""

from __future__ import annotations

EmailStr = str
