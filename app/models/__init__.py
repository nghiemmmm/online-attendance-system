"""Expose application database and schema models."""

from sqlmodel import SQLModel

from app.models.anhdiemdanh import (
    AnhDiemDanh,
    AnhDiemDanhBase,
    AnhDiemDanhCreate,
    AnhDiemDanhPublic,
    AnhDiemDanhsPublic,
    AnhDiemDanhUpdate,
)
from app.models.anhkhuonmat import (
    AnhKhuonMat,
    AnhKhuonMatBase,
    AnhKhuonMatCreate,
    AnhKhuonMatPublic,
    AnhKhuonMatsPublic,
    AnhKhuonMatUpdate,
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
from app.models.buoihoc import (
    BuoiHoc,
    BuoiHocBase,
    BuoiHocCreate,
    BuoiHocPublic,
    BuoiHocsPublic,
    BuoiHocUpdate,
)
from app.models.canhbaohoc_tap import CanhBaoVangItem, CanhBaoVangPublic
from app.models.canbo import (
    CanBo,
    CanBoBase,
    CanBoCreate,
    CanBoPublic,
    CanBosPublic,
    CanBoUpdate,
    StaffClassSectionItem,
    StaffClassSectionsPublic,
    AttendanceReportDataPoint,
    StaffAttendanceReportItem,
)
from app.models.common import Message
from app.models.dangkyhocphan import (
    DangKyHocPhan,
    DangKyHocPhanBase,
    DangKyHocPhanCreate,
    DangKyHocPhanPublic,
    DangKyHocPhansPublic,
    DangKyHocPhanUpdate,
)
from app.models.diemdanh import (
    DiemDanh,
    DiemDanhBase,
    DiemDanhCreate,
    DiemDanhPublic,
    DiemDanhsPublic,
    DiemDanhUpdate,
)
from app.models.diemdanh_summary import TongBuoiCoMatHocKyPublic
from app.models.hocphan import (
    HocPhan,
    HocPhanBase,
    HocPhanCreate,
    HocPhanPublic,
    HocPhansPublic,
    HocPhanUpdate,
)
from app.models.khieunai import (
    KhieuNai,
    KhieuNaiBase,
    KhieuNaiCanXuLyDetail,
    KhieuNaiCanXuLyItem,
    KhieuNaiCanXuLysPublic,
    KhieuNaiChapThuanRequest,
    KhieuNaiChoXuLyMetric,
    KhieuNaiCreate,
    KhieuNaiPublic,
    KhieuNaisPublic,
    KhieuNaiUpdate,
    KhieuNaiXuLyRequest,
    KhieuNaiXuLyResult,
)
from app.models.lophocphan import (
    LopHocPhan,
    LopHocPhanBase,
    LopHocPhanCreate,
    LopHocPhanPublic,
    LopHocPhansPublic,
    LopHocPhanUpdate,
)
from app.models.lichday import (
    BuoiHocGanDayItem,
    BuoiHocGanDaysPublic,
    LichDayItem,
    LichDaysPublic,
    SoLuongLopHocPhanDangDayPublic,
)
from app.models.lichhoc import LichHocHomNayItem, LichHocHomNayPublic
from app.models.nganh import (
    Nganh,
    NganhBase,
    NganhCreate,
    NganhPublic,
    NganhsPublic,
    NganhUpdate,
)
from app.models.oauth_identity import OAuthIdentity
from app.models.refresh_token import RefreshToken
from app.models.sinhvien import (
    SinhVien,
    SinhVienBase,
    SinhVienCreate,
    SinhVienPublic,
    SinhViensPublic,
    SinhVienUpdate,
    StudentScheduleItem,
    StudentSchedulePublic,
    StudentAttendanceItem,
    StudentAttendancePublic,
    StudentAvailableClassItem,
    StudentAvailableClassPublic,
)
from app.models.taikhoan import (
    TaiKhoan,
    TaiKhoanBase,
    TaiKhoanCreate,
    TaiKhoanListPublic,
    TaiKhoanProfile,
    TaiKhoanPublic,
    TaiKhoanRegister,
    TaiKhoansPublic,
    TaiKhoanUpdate,
)
from app.models.thoikhoabieu import (
    ThoiKhoaBieu,
    ThoiKhoaBieuBase,
    ThoiKhoaBieuCreate,
    ThoiKhoaBieuPublic,
    ThoiKhoaBieusPublic,
    ThoiKhoaBieuUpdate,
)

__all__ = [name for name in globals() if not name.startswith("_")]
