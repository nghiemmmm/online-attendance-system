"""
KhieuNai CRUD operations.

Contains database queries related to complaint records and complaint metrics.
"""

from datetime import datetime

from sqlmodel import Session, func, select

from app.models import (
    BuoiHoc,
    DiemDanh,
    HocPhan,
    KhieuNai,
    KhieuNaiCanXuLyDetail,
    KhieuNaiCanXuLyItem,
    LopHocPhan,
    SinhVien,
)

TRANG_THAI_CHO_XU_LY = "CHO_XU_LY"
TRANG_THAI_DA_CHAP_THUAN = "DA_CHAP_THUAN"
TRANG_THAI_DA_TU_CHOI = "DA_TU_CHOI"


def count_khieu_nai_cho_xu_ly_by_can_bo(
    *, session: Session, ma_can_bo: int
) -> int:
    """
    Count pending complaints in classes taught by a staff member.

    Args:
        session: Database session.
        ma_can_bo: Staff/teacher identifier.

    Returns:
        Number of pending complaints for class sections owned by the staff member.
    """
    statement = (
        select(func.count())
        .select_from(KhieuNai)
        .join(DiemDanh, KhieuNai.ma_diem_danh == DiemDanh.ma_diem_danh)
        .join(BuoiHoc, DiemDanh.ma_buoi_hoc == BuoiHoc.ma_buoi_hoc)
        .join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .where(
            LopHocPhan.ma_can_bo == ma_can_bo,
            KhieuNai.trang_thai == TRANG_THAI_CHO_XU_LY,
            KhieuNai.ngay_xu_ly.is_(None),
        )
    )
    return session.exec(statement).one()


def build_ho_ten_sinh_vien(sinh_vien: SinhVien | None) -> str | None:
    """Build student full name for complaint response data."""
    if not sinh_vien:
        return None
    return " ".join(part for part in [sinh_vien.ho, sinh_vien.ten] if part)


def build_khieu_nai_can_xu_ly_item(
    *,
    khieu_nai: KhieuNai,
    diem_danh: DiemDanh,
    buoi_hoc: BuoiHoc,
    lop_hoc_phan: LopHocPhan,
    hoc_phan: HocPhan | None,
    sinh_vien: SinhVien | None,
) -> KhieuNaiCanXuLyItem:
    """Map joined complaint data to a pending complaint list item."""
    return KhieuNaiCanXuLyItem(
        ma_khieu_nai=khieu_nai.ma_khieu_nai,
        ma_diem_danh=khieu_nai.ma_diem_danh,
        ma_sinh_vien=khieu_nai.ma_sinh_vien,
        ho_ten_sinh_vien=build_ho_ten_sinh_vien(sinh_vien),
        ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
        ten_hoc_phan=hoc_phan.ten_hoc_phan if hoc_phan else None,
        ngay_hoc=buoi_hoc.ngay_hoc,
        trang_thai_diem_danh=diem_danh.trang_thai,
        ly_do=khieu_nai.ly_do,
        ngay_gui=khieu_nai.ngay_gui,
        so_buoi=buoi_hoc.so_buoi,
    )


def build_khieu_nai_can_xu_ly_detail(
    *,
    khieu_nai: KhieuNai,
    diem_danh: DiemDanh,
    buoi_hoc: BuoiHoc,
    lop_hoc_phan: LopHocPhan,
    hoc_phan: HocPhan | None,
    sinh_vien: SinhVien | None,
) -> KhieuNaiCanXuLyDetail:
    """Map joined complaint data to a pending complaint detail response."""
    return KhieuNaiCanXuLyDetail(
        ma_khieu_nai=khieu_nai.ma_khieu_nai,
        ma_diem_danh=khieu_nai.ma_diem_danh,
        ma_sinh_vien=khieu_nai.ma_sinh_vien,
        ho_ten_sinh_vien=build_ho_ten_sinh_vien(sinh_vien),
        ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
        ten_hoc_phan=hoc_phan.ten_hoc_phan if hoc_phan else None,
        ngay_hoc=buoi_hoc.ngay_hoc,
        trang_thai_diem_danh=diem_danh.trang_thai,
        ly_do=khieu_nai.ly_do,
        trang_thai=khieu_nai.trang_thai,
        ngay_gui=khieu_nai.ngay_gui,
        ghi_chu_xu_ly=khieu_nai.ghi_chu_xu_ly,
        so_buoi=buoi_hoc.so_buoi,
    )


def get_khieu_nai_joined_rows_by_can_bo(
    *,
    session: Session,
    ma_can_bo: int,
    pending_only: bool = False,
    ma_khieu_nai: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[tuple[KhieuNai, DiemDanh, BuoiHoc, LopHocPhan, HocPhan, SinhVien]]:
    """Query complaint rows joined with attendance, lesson, class, subject and student."""
    statement = (
        select(KhieuNai, DiemDanh, BuoiHoc, LopHocPhan, HocPhan, SinhVien)
        .join(DiemDanh, KhieuNai.ma_diem_danh == DiemDanh.ma_diem_danh)
        .join(BuoiHoc, DiemDanh.ma_buoi_hoc == BuoiHoc.ma_buoi_hoc)
        .join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .join(HocPhan, LopHocPhan.ma_hoc_phan == HocPhan.ma_hoc_phan)
        .join(SinhVien, KhieuNai.ma_sinh_vien == SinhVien.ma_sinh_vien)
        .where(LopHocPhan.ma_can_bo == ma_can_bo)
        .order_by(KhieuNai.ngay_gui.desc(), KhieuNai.ma_khieu_nai.desc())
    )
    if pending_only:
        statement = statement.where(
            KhieuNai.trang_thai == TRANG_THAI_CHO_XU_LY,
            KhieuNai.ngay_xu_ly.is_(None),
        )
    if ma_khieu_nai is not None:
        statement = statement.where(KhieuNai.ma_khieu_nai == ma_khieu_nai)
    if ma_khieu_nai is None:
        statement = statement.offset(skip).limit(limit)

    return session.exec(statement).all()


def count_khieu_nai_can_xu_ly_by_can_bo(
    *, session: Session, ma_can_bo: int
) -> int:
    """Count pending complaints that belong to classes owned by a staff member."""
    statement = (
        select(func.count())
        .select_from(KhieuNai)
        .join(DiemDanh, KhieuNai.ma_diem_danh == DiemDanh.ma_diem_danh)
        .join(BuoiHoc, DiemDanh.ma_buoi_hoc == BuoiHoc.ma_buoi_hoc)
        .join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .where(
            LopHocPhan.ma_can_bo == ma_can_bo,
            KhieuNai.trang_thai == TRANG_THAI_CHO_XU_LY,
            KhieuNai.ngay_xu_ly.is_(None),
        )
    )
    return session.exec(statement).one()


def get_khieu_nai_can_xu_ly_by_can_bo(
    *,
    session: Session,
    ma_can_bo: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[KhieuNaiCanXuLyItem], int]:
    """Get pending complaints for a staff member."""
    rows = get_khieu_nai_joined_rows_by_can_bo(
        session=session,
        ma_can_bo=ma_can_bo,
        pending_only=True,
        skip=skip,
        limit=limit,
    )
    items = [
        build_khieu_nai_can_xu_ly_item(
            khieu_nai=khieu_nai,
            diem_danh=diem_danh,
            buoi_hoc=buoi_hoc,
            lop_hoc_phan=lop_hoc_phan,
            hoc_phan=hoc_phan,
            sinh_vien=sinh_vien,
        )
        for khieu_nai, diem_danh, buoi_hoc, lop_hoc_phan, hoc_phan, sinh_vien in rows
    ]
    count = count_khieu_nai_can_xu_ly_by_can_bo(
        session=session,
        ma_can_bo=ma_can_bo,
    )
    return items, count


def get_khieu_nai_detail_context_by_can_bo(
    *,
    session: Session,
    ma_can_bo: int,
    ma_khieu_nai: int,
) -> tuple[KhieuNai, DiemDanh, BuoiHoc, LopHocPhan, HocPhan, SinhVien] | None:
    """Get one complaint joined row if it belongs to a staff member."""
    rows = get_khieu_nai_joined_rows_by_can_bo(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )
    return rows[0] if rows else None


def get_khieu_nai_can_xu_ly_detail_by_can_bo(
    *,
    session: Session,
    ma_can_bo: int,
    ma_khieu_nai: int,
) -> KhieuNaiCanXuLyDetail | None:
    """Get pending complaint detail for a staff member."""
    context = get_khieu_nai_detail_context_by_can_bo(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )
    if not context:
        return None
    khieu_nai, diem_danh, buoi_hoc, lop_hoc_phan, hoc_phan, sinh_vien = context
    if khieu_nai.trang_thai != TRANG_THAI_CHO_XU_LY or khieu_nai.ngay_xu_ly:
        return None
    return build_khieu_nai_can_xu_ly_detail(
        khieu_nai=khieu_nai,
        diem_danh=diem_danh,
        buoi_hoc=buoi_hoc,
        lop_hoc_phan=lop_hoc_phan,
        hoc_phan=hoc_phan,
        sinh_vien=sinh_vien,
    )


def update_khieu_nai_xu_ly(
    *,
    session: Session,
    khieu_nai: KhieuNai,
    diem_danh: DiemDanh,
    trang_thai_khieu_nai: str,
    ma_can_bo_xu_ly: int,
    ngay_xu_ly: datetime,
    ghi_chu_xu_ly: str | None = None,
    trang_thai_diem_danh_moi: str | None = None,
) -> KhieuNai:
    """Update complaint processing fields and optionally update attendance status."""
    khieu_nai.trang_thai = trang_thai_khieu_nai
    khieu_nai.ma_can_bo_xu_ly = ma_can_bo_xu_ly
    khieu_nai.ngay_xu_ly = ngay_xu_ly
    khieu_nai.ghi_chu_xu_ly = ghi_chu_xu_ly
    if trang_thai_diem_danh_moi:
        diem_danh.trang_thai = trang_thai_diem_danh_moi

    session.add(khieu_nai)
    session.add(diem_danh)
    session.commit()
    session.refresh(khieu_nai)
    session.refresh(diem_danh)
    return khieu_nai
