import sys
import os
sys.path.append(os.path.abspath("d:/TTCS"))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sqlmodel import Session, create_engine, select
from app.core.config import settings
from app.models import FaceImage, AttendanceImage
from app.storage.cloudinary_storage import CloudinaryStorageService
from app.utils.logger import logger

def migrate_face_images(session, storage):
    print("\n--- MIGRATING FACE IMAGES (PORTRAITS) ---")
    stmt = select(FaceImage).where(
        (FaceImage.storage_provider != "CLOUDINARY") | (FaceImage.storage_provider.is_(None))
    )
    records = session.exec(stmt).all()
    print(f"Tìm thấy {len(records)} ảnh chân dung cần chuyển đổi.")
    
    migrated_count = 0
    for rec in records:
        if not rec.image_path:
            print(f"Bỏ qua FaceImage ID {rec.image_id}: không có đường dẫn image_path.")
            continue
            
        local_path = rec.image_path.lstrip("/")
        if not os.path.exists(local_path):
            print(f"Cảnh báo: File local không tồn tại ở đường dẫn '{local_path}'. Bỏ qua.")
            continue
            
        try:
            print(f"Đang tải {local_path} lên Cloudinary...")
            with open(local_path, "rb") as f:
                file_bytes = f.read()
                
            filename = os.path.basename(local_path)
            # Perform upload to dataset folder
            metadata = storage.save_image(
                file_bytes=file_bytes,
                filename=filename,
                folder="online_attendance/dataset"
            )
            
            if metadata.get("storage_provider") == "CLOUDINARY":
                rec.storage_provider = "CLOUDINARY"
                rec.public_id = metadata.get("public_id")
                rec.secure_url = metadata.get("secure_url")
                rec.version = metadata.get("version")
                rec.file_size = metadata.get("file_size")
                rec.mime_type = metadata.get("mime_type")
                rec.width = metadata.get("width")
                rec.height = metadata.get("height")
                
                session.add(rec)
                session.commit()
                migrated_count += 1
                print(f"Thành công: Đã chuyển đổi FaceImage ID {rec.image_id} -> {rec.secure_url}")
            else:
                print(f"Thất bại: Upload Cloudinary cho FaceImage ID {rec.image_id} không thành công.")
        except Exception as e:
            print(f"Lỗi khi chuyển đổi FaceImage ID {rec.image_id}: {e}")
            session.rollback()
            
    print(f"Hoàn thành chuyển đổi {migrated_count}/{len(records)} ảnh chân dung.")

def migrate_attendance_images(session, storage):
    print("\n--- MIGRATING ATTENDANCE EVIDENCE IMAGES ---")
    stmt = select(AttendanceImage).where(
        (AttendanceImage.storage_provider != "CLOUDINARY") | (AttendanceImage.storage_provider.is_(None))
    )
    records = session.exec(stmt).all()
    print(f"Tìm thấy {len(records)} ảnh minh chứng cần chuyển đổi.")
    
    migrated_count = 0
    for rec in records:
        if not rec.image_path:
            print(f"Bỏ qua AttendanceImage ID {rec.image_id}: không có đường dẫn image_path.")
            continue
            
        local_path = rec.image_path.lstrip("/")
        if not os.path.exists(local_path):
            print(f"Cảnh báo: File local không tồn tại ở đường dẫn '{local_path}'. Bỏ qua.")
            continue
            
        try:
            print(f"Đang tải {local_path} lên Cloudinary...")
            with open(local_path, "rb") as f:
                file_bytes = f.read()
                
            filename = os.path.basename(local_path)
            # Perform upload to evidence folder
            metadata = storage.save_image(
                file_bytes=file_bytes,
                filename=filename,
                folder="online_attendance/evidence"
            )
            
            if metadata.get("storage_provider") == "CLOUDINARY":
                rec.storage_provider = "CLOUDINARY"
                rec.public_id = metadata.get("public_id")
                rec.secure_url = metadata.get("secure_url")
                rec.version = metadata.get("version")
                rec.file_size = metadata.get("file_size")
                rec.mime_type = metadata.get("mime_type")
                rec.width = metadata.get("width")
                rec.height = metadata.get("height")
                
                session.add(rec)
                session.commit()
                migrated_count += 1
                print(f"Thành công: Đã chuyển đổi AttendanceImage ID {rec.image_id} -> {rec.secure_url}")
            else:
                print(f"Thất bại: Upload Cloudinary cho AttendanceImage ID {rec.image_id} không thành công.")
        except Exception as e:
            print(f"Lỗi khi chuyển đổi AttendanceImage ID {rec.image_id}: {e}")
            session.rollback()
            
    print(f"Hoàn thành chuyển đổi {migrated_count}/{len(records)} ảnh minh chứng.")

def main():
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    storage = CloudinaryStorageService()
    
    with Session(engine) as session:
        migrate_face_images(session, storage)
        migrate_attendance_images(session, storage)
        
    print("\nQuá trình chuyển đổi dữ liệu lưu trữ đã kết thúc thành công!")

if __name__ == "__main__":
    main()
