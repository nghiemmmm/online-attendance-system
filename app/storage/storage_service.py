import abc
from typing import Any


class StorageService(abc.ABC):
    """Abstract Base Class for image storage operations."""

    @abc.abstractmethod
    def save_image(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str,
        public_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Save/Upload an image.

        Args:
            file_bytes: Raw image file bytes.
            filename: Original file name.
            folder: Remote directory/folder path.
            public_id: Optional fixed public ID.

        Returns:
            Dict containing metadata:
                - storage_provider: str
                - public_id: str
                - image_path: str | None
                - secure_url: str
                - file_size: int | None
                - mime_type: str | None
                - width: int | None
                - height: int | None
                - version: str | None
        """
        pass

    @abc.abstractmethod
    def delete_image(self, public_id: str, local_path: str | None = None) -> bool:
        """
        Delete an image from storage.

        Args:
            public_id: The remote public ID.
            local_path: Optional local file path if fallback or local provider.

        Returns:
            True if deletion was successful, False otherwise.
        """
        pass

    @abc.abstractmethod
    def get_image_url(self, public_id: str, local_path: str | None = None) -> str:
        """
        Get the public retrieval URL for an image.

        Args:
            public_id: The remote public ID.
            local_path: Optional local file path.

        Returns:
            Publicly accessible URL.
        """
        pass
