from app.core.config import settings
from app.utils.logger import logger


def _load_cloudinary():
    try:
        import cloudinary
        import cloudinary.api  # noqa: F401
        import cloudinary.uploader  # noqa: F401
    except ImportError as exc:
        logger.warning("Cloudinary SDK is not installed: %s", exc)
        return None
    return cloudinary


def init_cloudinary():
    """Configure Cloudinary SDK."""
    cloudinary = _load_cloudinary()
    if cloudinary is None:
        return False

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    return True



init_cloudinary()

def upload_to_cloudinary(file_bytes: bytes, folder: str = "online_attendance/faces", public_id: str | None = None) -> str | None:
    """
    Upload image bytes to Cloudinary and return the secure HTTPS URL.
    Fallback to local file if Cloudinary fails or credentials not provided.
    """
    try:
        cloudinary = _load_cloudinary()
        if cloudinary is None:
            return None

        init_cloudinary()
        options = {"folder": folder, "resource_type": "image"}
        if public_id:
            options["public_id"] = public_id
            options["overwrite"] = True
            
        result = cloudinary.uploader.upload(file_bytes, **options)
        return result.get("secure_url")
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        return None

def delete_from_cloudinary(public_id: str) -> bool:
    """Delete an image from Cloudinary by its public ID."""
    try:
        cloudinary = _load_cloudinary()
        if cloudinary is None:
            return False

        init_cloudinary()
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        logger.error(f"Cloudinary delete failed: {e}")
        return False
