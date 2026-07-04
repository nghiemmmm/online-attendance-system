"""Expose application database and schema models."""

from sqlmodel import SQLModel

from app.models.attendance_image import (
    AttendanceImage,
    AttendanceImageBase,
    AttendanceImageCreate,
    AttendanceImagePublic,
    AttendanceImagesPublic,
    AttendanceImageUpdate,
)
from app.models.face_image import (
    FaceImage,
    FaceImageBase,
    FaceImageCreate,
    FaceImagePublic,
    FaceImagesPublic,
    FaceImageUpdate,
)
from app.models.attendance_summary import MonthlyAttendanceSummary
from app.models.audit_log import (
    AuditLog,
    AuditLogBase,
    AuditLogCreate,
    AuditLogPublic,
    AuditLogsPublic,
)
from app.models.auth import (
    GoogleAuthPending,
    LoginRequest,
    LogoutRequest,
    NewPassword,
    RefreshTokenRequest,
    Token,
    TokenPayload,
    UpdatePassword,
)
from app.models.otp import (
    OTPRecord,
    SendOtpRequest,
    StudentRegisterRequest,
)
from app.models.class_session import (
    ClassSession,
    ClassSessionBase,
    ClassSessionCreate,
    ClassSessionPublic,
    ClassSessionsPublic,
    ClassSessionUpdate,
)
from app.models.academic_warning import AbsenceWarningItem, AbsenceWarningsPublic
from app.models.staff import (
    Staff,
    StaffBase,
    StaffCreate,
    StaffPublic,
    StaffMembersPublic,
    StaffUpdate,
    StaffClassSectionItem,
    StaffClassSectionsPublic,
    AttendanceReportDataPoint,
    StaffAttendanceReportItem,
)
from app.models.common import Message
from app.models.course_registration import (
    CourseRegistration,
    CourseRegistrationBase,
    CourseRegistrationCreate,
    CourseRegistrationPublic,
    CourseRegistrationsPublic,
    CourseRegistrationUpdate,
)
from app.models.attendance import (
    Attendance,
    AttendanceBase,
    AttendanceCreate,
    AttendancePublic,
    AttendancesPublic,
    AttendanceUpdate,
)
from app.models.attendance_statistics import SemesterAttendanceSummaryPublic
from app.models.course import (
    Course,
    CourseBase,
    CourseCreate,
    CoursePublic,
    CoursesPublic,
    CourseUpdate,
)
from app.models.appeal import (
    Appeal,
    AppealBase,
    PendingAppealDetail,
    PendingAppealItem,
    PendingAppealsPublic,
    AppealApprovalRequest,
    PendingAppealMetric,
    AppealCreate,
    AppealPublic,
    AppealsPublic,
    AppealUpdate,
    AppealResolutionRequest,
    AppealResolutionResult,
)
from app.models.class_section import (
    ClassSection,
    ClassSectionBase,
    ClassSectionCreate,
    ClassSectionPublic,
    ClassSectionsPublic,
    ClassSectionUpdate,
)
from app.models.teaching_schedule import (
    RecentClassSessionItem,
    RecentClassSessionsPublic,
    TeachingScheduleItem,
    TeachingSchedulesPublic,
    ActiveClassSectionCountPublic,
)
from app.models.student_schedule import TodayScheduleItem, TodaySchedulePublic
from app.models.major import (
    Major,
    MajorBase,
    MajorCreate,
    MajorPublic,
    MajorsPublic,
    MajorUpdate,
)
from app.models.oauth_identity import OAuthIdentity
from app.models.refresh_token import RefreshToken
from app.models.student import (
    Student,
    StudentBase,
    StudentCreate,
    StudentPublic,
    StudentsPublic,
    StudentUpdate,
    StudentScheduleItem,
    StudentSchedulePublic,
    StudentAttendanceItem,
    StudentAttendancePublic,
    StudentAvailableClassItem,
    StudentAvailableClassPublic,
)
from app.models.account import (
    Account,
    AccountBase,
    AccountCreate,
    AccountListPublic,
    AccountProfile,
    AccountPublic,
    AccountRegister,
    AccountsPublic,
    AccountUpdate,
)
from app.models.timetable import (
    Timetable,
    TimetableBase,
    TimetableCreate,
    TimetablePublic,
    TimetablesPublic,
    TimetableUpdate,
)
from app.models.semester import (
    Semester,
    SemesterBase,
    SemesterCreate,
    SemesterPublic,
    SemestersPublic,
    SemesterUpdate,
)

# Backward-compatible aliases for legacy Vietnamese model names.
TaiKhoan = Account
TaiKhoanBase = AccountBase
TaiKhoanCreate = AccountCreate
TaiKhoanPublic = AccountPublic
TaiKhoanListPublic = AccountsPublic
TaiKhoanProfile = AccountProfile
TaiKhoanRegister = AccountRegister
TaiKhoanUpdate = AccountUpdate

SinhVien = Student
SinhVienBase = StudentBase
SinhVienCreate = StudentCreate
SinhVienPublic = StudentPublic
SinhVienUpdate = StudentUpdate

CanBo = Staff
CanBoBase = StaffBase
CanBoCreate = StaffCreate
CanBoPublic = StaffPublic
CanBoUpdate = StaffUpdate

AnhKhuonMat = FaceImage
AnhKhuonMatBase = FaceImageBase
AnhKhuonMatCreate = FaceImageCreate
AnhKhuonMatPublic = FaceImagePublic
AnhKhuonMatUpdate = FaceImageUpdate

Nganh = Major
NganhBase = MajorBase
NganhCreate = MajorCreate
NganhPublic = MajorPublic
NganhUpdate = MajorUpdate

__all__ = [name for name in globals() if not name.startswith("_")]
