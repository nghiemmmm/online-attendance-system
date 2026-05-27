import logging

from PIL import Image

from app.services.models import face_encodings, face_locations

logger = logging.getLogger(__name__)


def _build_error(frame_index, code, message):
    return {
        "frame_index": frame_index,
        "boxes": [],
        "error": code,
        "error_message": message,
    }


async def detect_user(video_transform_track, max_frames=30):
    if video_transform_track is None:
        raise ValueError("video_transform_track must not be None")
    if not hasattr(video_transform_track, "recv"):
        raise ValueError("video_transform_track must provide async recv()")
    if not isinstance(max_frames, int) or max_frames <= 0:
        raise ValueError("max_frames must be a positive integer")

    results = []
    for frame_index in range(1, max_frames + 1):
        try:
            frame = await video_transform_track.recv()
            if frame is None:
                results.append(
                    _build_error(frame_index, "empty_frame", "Track returned None frame")
                )
                continue

            rgb = frame.to_ndarray(format="rgb24")
            pil_image = Image.fromarray(rgb)
            boxes = face_locations(pil_image) or []
            results.append({"frame_index": frame_index, "boxes": boxes})
        except Exception as exc:
            logger.exception("Face detection failed at frame %s", frame_index)
            results.append(_build_error(frame_index, "detect_failed", str(exc)))

    return results


async def verify_face(results, min_detected_frames=3, min_face_ratio=0.3):
    if not isinstance(results, list):
        raise ValueError("results must be a list")
    if not results:
        return {
            "verified": False,
            "reason": "no_results",
            "total_frames": 0,
            "detected_frames": 0,
            "face_ratio": 0.0,
        }
    if not isinstance(min_detected_frames, int) or min_detected_frames <= 0:
        raise ValueError("min_detected_frames must be a positive integer")
    if not isinstance(min_face_ratio, (float, int)) or not (
        0 < float(min_face_ratio) <= 1
    ):
        raise ValueError("min_face_ratio must be in range (0, 1]")

    total_frames = len(results)
    detected_frames = 0
    error_frames = 0

    for item in results:
        if not isinstance(item, dict):
            error_frames += 1
            continue

        boxes = item.get("boxes")
        if isinstance(boxes, list) and len(boxes) > 0:
            detected_frames += 1
        if item.get("error"):
            error_frames += 1

    face_ratio = detected_frames / total_frames if total_frames else 0.0
    verified = detected_frames >= min_detected_frames and face_ratio >= float(
        min_face_ratio
    )

    return {
        "verified": verified,
        "total_frames": total_frames,
        "detected_frames": detected_frames,
        "error_frames": error_frames,
        "face_ratio": round(face_ratio, 4),
        "thresholds": {
            "min_detected_frames": min_detected_frames,
            "min_face_ratio": float(min_face_ratio),
        },
    }


async def verify_face_and_extract_embeddings(
    video_transform_track,
    max_frames=30,
    min_detected_frames=3,
    min_face_ratio=0.3,
    max_embeddings=20,
):
    if not isinstance(max_embeddings, int) or max_embeddings <= 0:
        raise ValueError("max_embeddings must be a positive integer")
    if video_transform_track is None:
        raise ValueError("video_transform_track must not be None")
    if not hasattr(video_transform_track, "recv"):
        raise ValueError("video_transform_track must provide async recv()")
    if not isinstance(max_frames, int) or max_frames <= 0:
        raise ValueError("max_frames must be a positive integer")

    results = []
    embeddings = []

    for frame_index in range(1, max_frames + 1):
        try:
            frame = await video_transform_track.recv()
            if frame is None:
                results.append(
                    _build_error(frame_index, "empty_frame", "Track returned None frame")
                )
                continue

            rgb = frame.to_ndarray(format="rgb24")
            pil_image = Image.fromarray(rgb)
            boxes = face_locations(pil_image) or []
            frame_result = {"frame_index": frame_index, "boxes": boxes}

            if boxes and len(embeddings) < max_embeddings:
                frame_embeddings = face_encodings(pil_image, known_face_locations=boxes)
                if frame_embeddings:
                    remaining = max_embeddings - len(embeddings)
                    for emb in frame_embeddings[:remaining]:
                        try:
                            embeddings.append(emb.tolist())
                        except Exception:
                            embeddings.append(list(emb))

            results.append(frame_result)
        except Exception as exc:
            logger.exception("Verify+embedding failed at frame %s", frame_index)
            results.append(
                _build_error(frame_index, "verify_embedding_failed", str(exc))
            )

    verify_summary = await verify_face(
        results,
        min_detected_frames=min_detected_frames,
        min_face_ratio=min_face_ratio,
    )

    return {
        **verify_summary,
        "embedding_count": len(embeddings),
        "embeddings": embeddings,
        "results": results,
    }
