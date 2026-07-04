import asyncio
import io
import time

from aiortc import MediaStreamTrack
from PIL import Image
from sqlmodel import Session

# To call db we need session
from app.core.db import engine
from app.crud.attendance_crud import mark_attendance_by_lora
from app.services.face_service import face_service
from app.utils.logger import logger


class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from another track and runs AI periodically.
    """

    kind = "video"

    def __init__(self, track, class_session_id: int = None):
        super().__init__()
        self.track = track
        self.class_session_id = class_session_id
        self.last_process_time = time.time()
        self.process_interval = 3.0  # Xử lý 3 giây 1 lần

    def _process_frame_sync(self, frame) -> None:
        """Process video frame and register attendance synchronously in a worker thread."""
        try:
            # Chuyển frame thành ảnh
            img = frame.to_ndarray(format="rgb24")
            pil_img = Image.fromarray(img)
            img_byte_arr = io.BytesIO()
            pil_img.save(img_byte_arr, format="JPEG")
            image_bytes = img_byte_arr.getvalue()

            # Chạy nhận diện
            recognized_ids = face_service.recognize_faces(image_bytes)

            if recognized_ids:
                # Lọc trùng lặp ghi nhận điểm danh (Debounce) bằng Redis Cache
                filtered_ids = []
                try:
                    import redis

                    from app.core.config import settings

                    r = redis.from_url(
                        settings.REDIS_URL, socket_timeout=2.0, decode_responses=True
                    )
                    for s_id in recognized_ids:
                        key = f"attendance:checked:{self.class_session_id}:{s_id}"
                        # set if not exists, TTL 300 seconds (5 minutes)
                        if r.set(key, "1", ex=300, nx=True):
                            filtered_ids.append(s_id)
                        else:
                            logger.info(
                                f"Student ID {s_id} check-in debounced by Redis cache."
                            )
                except Exception as e:
                    logger.error(
                        f"Redis check-in debounce error: {e}. Falling back to direct database write."
                    )
                    filtered_ids = recognized_ids

                if filtered_ids:
                    # Ghi điểm danh
                    with Session(engine) as session:
                        result = mark_attendance_by_lora(
                            session=session,
                            class_session_id=self.class_session_id,
                            student_ids=filtered_ids,
                            average_confidence=0.8,
                        )
                        logger.info(f"WebRTC AI Diem danh: {result}")
        except Exception as e:
            logger.error(f"Error processing frame in background thread: {e}")

    async def recv(self):
        frame = await self.track.recv()

        current_time = time.time()
        if self.class_session_id and (
            current_time - self.last_process_time > self.process_interval
        ):
            self.last_process_time = current_time
            # Run CPU-bound AI processing in a separate thread pool to prevent async loop blocking
            asyncio.create_task(asyncio.to_thread(self._process_frame_sync, frame))

        return frame
