import os
import time
import io
from PIL import Image
from typing import Any, Dict

from app.storage.storage_service import StorageService
from app.storage.local_storage import LocalStorageService
from app.utils.cloudinary import upload_to_cloudinary, delete_from_cloudinary
from app.utils.logger import logger

class CloudinaryStorageService(StorageService):
    """Cloudinary Implementation of StorageService with local fallback."""

    def __init__(self) -> None:
        self.local_fallback = LocalStorageService()

    def save_image(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str,
        public_id: str | None = None
    ) -> Dict[str, Any]:
        max_retries = 3
        backoff_sec = 1
        
        target_public_id = None
        if public_id:
            target_public_id = public_id
            if "." in target_public_id:
                target_public_id = os.path.splitext(target_public_id)[0]
        else:
            target_public_id = os.path.splitext(filename)[0]

        # Clean folder names and make public_id unique but clean
        clean_folder = folder.replace("\\", "/").strip("/")

        upload_success = False
        secure_url = None
        
        for attempt in range(1, max_retries + 1):
            try:
                secure_url = upload_to_cloudinary(
                    file_bytes=file_bytes,
                    folder=clean_folder,
                    public_id=target_public_id
                )
                if secure_url:
                    upload_success = True
                    break
            except Exception as e:
                logger.error(f"Cloudinary upload attempt {attempt} failed: {e}")
                
            if attempt < max_retries:
                logger.info(f"Retrying Cloudinary upload in {backoff_sec}s...")
                time.sleep(backoff_sec)
                backoff_sec *= 2

        if upload_success and secure_url:
            width, height = None, None
            try:
                with Image.open(io.BytesIO(file_bytes)) as img:
                    width, height = img.size
            except Exception:
                pass
                
            full_public_id = f"{clean_folder}/{target_public_id}".replace("//", "/")
            
            return {
                "storage_provider": "CLOUDINARY",
                "public_id": full_public_id,
                "image_path": None,
                "secure_url": secure_url,
                "file_size": len(file_bytes),
                "mime_type": "image/jpeg",
                "width": width,
                "height": height,
                "version": None
            }
        else:
            logger.warning("Cloudinary upload completely failed. Falling back to local storage.")
            return self.local_fallback.save_image(file_bytes, filename, folder, public_id)

    def delete_image(self, public_id: str, local_path: str | None = None) -> bool:
        deleted_local = False
        if local_path and os.path.exists(local_path):
            deleted_local = self.local_fallback.delete_image(public_id, local_path)
            
        # If public_id is a local path (starts with local directories), delete locally
        if public_id and (public_id.startswith("uploads/") or public_id.startswith("dataset/")):
            deleted_local = deleted_local or self.local_fallback.delete_image(public_id, None)
            return deleted_local

        if public_id:
            try:
                result = delete_from_cloudinary(public_id)
                return result or deleted_local
            except Exception as e:
                logger.error(f"Cloudinary delete failed for {public_id}: {e}")
                return deleted_local
        return deleted_local

    def get_image_url(self, public_id: str, local_path: str | None = None) -> str:
        if local_path or (public_id and (public_id.startswith("uploads/") or public_id.startswith("dataset/"))):
            return self.local_fallback.get_image_url(public_id, local_path)
            
        from app.core.config import settings
        cloud_name = settings.CLOUDINARY_CLOUD_NAME
        if not cloud_name:
            return f"https://res.cloudinary.com/dtdkqzqvo/image/upload/{public_id}"
        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}"
