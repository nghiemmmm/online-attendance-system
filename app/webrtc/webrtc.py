import time
import io
from aiortc import MediaStreamTrack
import av
from PIL import Image

from app.services.face_service import face_service

# To call db we need session
from app.core.db import engine
from sqlmodel import Session
from app.crud.diemdanh_crud import diem_danh_tu_dong_lo

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from another track and runs AI periodically.
    """

    kind = "video"

    def __init__(self, track, ma_buoi_hoc: int = None):
        super().__init__()
        self.track = track
        self.ma_buoi_hoc = ma_buoi_hoc
        self.last_process_time = time.time()
        self.process_interval = 3.0  # Xử lý 3 giây 1 lần

    async def recv(self):
        frame = await self.track.recv()
        
        current_time = time.time()
        if self.ma_buoi_hoc and (current_time - self.last_process_time > self.process_interval):
            self.last_process_time = current_time
            # Chuyển frame thành ảnh
            img = frame.to_ndarray(format="rgb24")
            pil_img = Image.fromarray(img)
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format='JPEG')
            image_bytes = img_byte_arr.getvalue()
            
            # Chạy nhận diện
            recognized_ids = face_service.recognize_faces(image_bytes)
            
            if recognized_ids:
                # Ghi điểm danh
                with Session(engine) as session:
                    result = diem_danh_tu_dong_lo(
                        session=session,
                        ma_buoi_hoc=self.ma_buoi_hoc,
                        danh_sach_ma_sinh_vien=recognized_ids,
                        do_tin_cay_trung_binh=0.8
                    )
                    print(f"WebRTC AI Diem danh: {result}")

        return frame
