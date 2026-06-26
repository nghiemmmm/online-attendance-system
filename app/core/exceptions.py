class AppException(Exception):
    """Base application exception."""
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None, status_code: int | None = None):
        super().__init__(detail or self.detail)
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code


# 404 Not Found Exceptions
class StudentNotFoundError(AppException):
    status_code = 404
    detail = "Student profile not found"


class StaffNotFoundError(AppException):
    status_code = 404
    detail = "Staff member not found"


class ClassSectionNotFoundError(AppException):
    status_code = 404
    detail = "Class section not found"


class LessonNotFoundError(AppException):
    status_code = 404
    detail = "Lesson not found"


class TimetableNotFoundError(AppException):
    status_code = 404
    detail = "Timetable not found"


class CourseNotFoundError(AppException):
    status_code = 404
    detail = "Course not found"


class MajorNotFoundError(AppException):
    status_code = 404
    detail = "Major not found"


class AppealNotFoundError(AppException):
    status_code = 404
    detail = "Appeal not found"


class FaceImageNotFoundError(AppException):
    status_code = 404
    detail = "Face image not found"


class CourseRegistrationNotFoundError(AppException):
    status_code = 404
    detail = "Course registration not found"


# 400 Bad Request & 409 Conflict Exceptions
class StudentAlreadyExistsError(AppException):
    status_code = 409
    detail = "Student profile already exists"


class StaffAlreadyExistsError(AppException):
    status_code = 409
    detail = "Staff profile already exists"


class DuplicateAppealError(AppException):
    status_code = 400
    detail = "Đã tồn tại khiếu nại cho bản ghi điểm danh này"


class DuplicateRegistrationError(AppException):
    status_code = 409
    detail = "Duplicate registration"


class AppealTimeLimitExceededError(AppException):
    status_code = 400
    detail = "Đã quá thời hạn 48 giờ để gửi khiếu nại"


class LessonClosedError(AppException):
    status_code = 400
    detail = "Khong the mo buoi hoc da huy"


class LessonCompletedError(AppException):
    status_code = 400
    detail = "Khong the huy buoi hoc da ket thuc"


class FaceQualityUnacceptableError(AppException):
    status_code = 400
    detail = "Ảnh không đạt yêu cầu chất lượng"


class InvalidFaceEmbeddingError(AppException):
    status_code = 400
    detail = "Ảnh chưa có embedding hợp lệ"


class CourseAlreadyExistsError(AppException):
    status_code = 409
    detail = "Course already exists"


class MajorAlreadyExistsError(AppException):
    status_code = 409
    detail = "Major already exists"


class AttendanceAlreadyExistsError(AppException):
    status_code = 409
    detail = "Attendance already exists"


# 403 Forbidden Exceptions
class PermissionDeniedError(AppException):
    status_code = 403
    detail = "Permission denied"
