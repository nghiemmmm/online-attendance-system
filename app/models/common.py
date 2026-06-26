"""Define shared API response models."""

from sqlmodel import SQLModel


class Message(SQLModel):
    """Represent a generic API message response."""

    message: str
