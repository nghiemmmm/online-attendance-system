"""Define shared API response models."""

from app.models.base import AppBaseModel


class Message(AppBaseModel):
    """Represent a generic API message response."""

    message: str
