import os
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
from app.core.db import engine
from app.models import AttendanceImage
from app.utils.cloudinary import delete_from_cloudinary
from app.utils.logger import logger

def cleanup_expired_attendance_evidence(days: int = 2) -> int:
    """
    Automatically delete attendance evidence images older than specified days (default: 2 days).
    Cleans up physical local files and Cloudinary images.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    deleted_count = 0
    
    with Session(engine) as session:
        statement = select(AttendanceImage).where(AttendanceImage.created_at < cutoff)
        expired_images = session.exec(statement).all()
        
        for img in expired_images:
            if img.image_path:
                # 1. Cloudinary cleanup
                if "cloudinary.com" in img.image_path:
                    try:
                        # Extract public_id from URL
                        parts = img.image_path.split("/")
                        upload_idx = parts.index("upload") if "upload" in parts else -1
                        if upload_idx != -1:
                            # e.g. v12345/folder/filename.jpg
                            public_id_with_ext = "/".join(parts[upload_idx+2:])
                            public_id = os.path.splitext(public_id_with_ext)[0]
                            delete_from_cloudinary(public_id)
                    except Exception as e:
                        logger.error(f"Failed to extract/delete Cloudinary public_id for {img.image_path}: {e}")
                else:
                    # 2. Local physical file cleanup
                    local_path = img.image_path.lstrip("/")
                    if os.path.exists(local_path):
                        try:
                            os.remove(local_path)
                        except Exception as e:
                            logger.error(f"Failed to remove local file {local_path}: {e}")
                            
            session.delete(img)
            deleted_count += 1
            
        session.commit()
        
    if deleted_count > 0:
        logger.info(f"Auto-cleanup: Removed {deleted_count} attendance evidence images older than {days} days.")
    return deleted_count
