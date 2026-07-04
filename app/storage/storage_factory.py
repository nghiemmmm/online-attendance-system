from app.core.config import settings
from app.storage.local_storage import LocalStorageService
from app.storage.storage_service import StorageService

_storage_instance: StorageService | None = None


def get_storage_service() -> StorageService:
    """
    Return the singleton StorageService instance based on config.
    """
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    provider = getattr(settings, "IMAGE_STORAGE_PROVIDER", "LOCAL").upper()
    if provider == "CLOUDINARY":
        from app.storage.cloudinary_storage import CloudinaryStorageService

        _storage_instance = CloudinaryStorageService()
    else:
        _storage_instance = LocalStorageService()

    return _storage_instance
