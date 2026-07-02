import os
import mimetypes
from typing import Any, Dict
from PIL import Image
import io

from app.storage.storage_service import StorageService

class LocalStorageService(StorageService):
    """Local Filesystem Implementation of StorageService."""

    def save_image(
        self,
        file_bytes: bytes,
        filename: str,
        folder: str,
        public_id: str | None = None
    ) -> Dict[str, Any]:
        # Determine the base directory based on folder name
        if "dataset" in folder:
            base_dir = "dataset"
        elif "evidence" in folder or "attendance" in folder:
            base_dir = os.path.join("uploads", "attendance")
        else:
            base_dir = os.path.join("uploads", folder)

        os.makedirs(base_dir, exist_ok=True)
        
        # Decide the filename/path
        if public_id:
            # If public_id is provided, make sure it is just the basename
            name = os.path.basename(public_id)
            if not name.endswith(".jpg") and not name.endswith(".png"):
                name += ".jpg"
        else:
            name = filename

        filepath = os.path.join(base_dir, name)
        
        # Save bytes
        with open(filepath, "wb") as f:
            f.write(file_bytes)
            
        file_size = len(file_bytes)
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = "image/jpeg"
            
        # Get image dimensions using PIL
        width, height = None, None
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                width, height = img.size
        except Exception:
            pass

        # Generate a relative URL that aligns with app mounts
        # "/uploads/..." or "/dataset/..."
        # If filepath starts with "uploads/", we serve it via "/uploads/..." mount
        # If it is in "dataset/", we serve it via "/dataset/..."
        normalized_path = filepath.replace("\\", "/")
        secure_url = "/" + normalized_path

        return {
            "storage_provider": "LOCAL",
            "public_id": normalized_path,
            "image_path": normalized_path,
            "secure_url": secure_url,
            "file_size": file_size,
            "mime_type": mime_type,
            "width": width,
            "height": height,
            "version": None
        }

    def delete_image(self, public_id: str, local_path: str | None = None) -> bool:
        path_to_delete = local_path or public_id
        if not path_to_delete:
            return False
            
        # Clean prefix slashes
        path_to_delete = path_to_delete.lstrip("/")
        if os.path.exists(path_to_delete):
            try:
                os.remove(path_to_delete)
                return True
            except Exception:
                return False
        return False

    def get_image_url(self, public_id: str, local_path: str | None = None) -> str:
        path = local_path or public_id
        if not path:
            return ""
        # Ensure it starts with /
        path = path.replace("\\", "/")
        if not path.startswith("/"):
            path = "/" + path
        return path
