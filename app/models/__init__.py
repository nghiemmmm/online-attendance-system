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
from app.models.auth import NewPassword, Token, TokenPayload, UpdatePassword
from app.models.buoihoc import (
    BuoiHoc,
    BuoiHocBase,
    BuoiHocCreate,
    BuoiHocPublic,
    BuoiHocsPublic,
    BuoiHocUpdate,
)
from app.models.canbo import (
    CanBo,
    CanBoBase,
    CanBoCreate,
    CanBoPublic,
    CanBosPublic,
    CanBoUpdate,
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
    KhieuNaiCreate,
    KhieuNaiPublic,
    KhieuNaisPublic,
    KhieuNaiUpdate,
)
from app.models.lophocphan import (
    LopHocPhan,
    LopHocPhanBase,
    LopHocPhanCreate,
    LopHocPhanPublic,
    LopHocPhansPublic,
    LopHocPhanUpdate,
)
from app.models.nganh import (
    Nganh,
    NganhBase,
    NganhCreate,
    NganhPublic,
    NganhsPublic,
    NganhUpdate,
)
from app.models.sinhvien import (
    SinhVien,
    SinhVienBase,
    SinhVienCreate,
    SinhVienPublic,
    SinhViensPublic,
    SinhVienUpdate,
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
