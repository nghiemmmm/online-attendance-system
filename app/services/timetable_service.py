"""Provide timetable application services."""

from typing import Any
from app.core.exceptions import TimetableNotFoundError, ClassSectionNotFoundError, PermissionDeniedError, LessonNotFoundError, LessonClosedError, LessonCompletedError, AppException
from sqlmodel import Session

from app.crud import thoikhoabieu_crud
from app.models import Message, ThoiKhoaBieu, ThoiKhoaBieuCreate, ThoiKhoaBieuUpdate


def list_timetables(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[ThoiKhoaBieu], int]:
    """Return paginated timetables."""
    return thoikhoabieu_crud.get_thoikhoabieus(
        session=session,
        skip=skip,
        limit=limit,
    )


def get_timetable_or_404(
    *,
    session: Session,
    ma_thoi_khoa_bieu: int,
) -> ThoiKhoaBieu:
    """Return a timetable or raise a 404 error."""
    item = thoikhoabieu_crud.get_thoikhoabieu(
        session=session,
        ma_thoi_khoa_bieu=ma_thoi_khoa_bieu,
    )
    if not item:
        raise TimetableNotFoundError()
    return item


def create_timetable(
    *,
    session: Session,
    item_in: ThoiKhoaBieuCreate,
) -> ThoiKhoaBieu:
    """Create a timetable."""
    return thoikhoabieu_crud.create_thoikhoabieu(
        session=session,
        item_create=item_in,
    )


def update_timetable(
    *,
    session: Session,
    ma_thoi_khoa_bieu: int,
    item_in: ThoiKhoaBieuUpdate,
) -> ThoiKhoaBieu:
    """Update a timetable."""
    item = get_timetable_or_404(
        session=session,
        ma_thoi_khoa_bieu=ma_thoi_khoa_bieu,
    )
    return thoikhoabieu_crud.update_thoikhoabieu(
        session=session,
        db_item=item,
        item_update=item_in,
    )


def delete_timetable(*, session: Session, ma_thoi_khoa_bieu: int) -> Message:
    """Delete a timetable."""
    item = get_timetable_or_404(
        session=session,
        ma_thoi_khoa_bieu=ma_thoi_khoa_bieu,
    )
    thoikhoabieu_crud.delete_thoikhoabieu(session=session, db_item=item)
    return Message(message="Timetable deleted successfully")


# Validation Helpers
def ensure_can_manage_lop_hoc_phan(
    *,
    session: Session,
    current_account: Any,
    ma_lop_hoc_phan: int,
) -> Any:
    from app.models import LopHocPhan
    from app.crud import canbo_crud
    
    lop_hoc_phan = session.get(LopHocPhan, ma_lop_hoc_phan)
    if not lop_hoc_phan:
        raise ClassSectionNotFoundError("Lop hoc phan khong ton tai")

    can_bo = canbo_crud.get_staff_member_by_account_id(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )
    if current_account.vai_tro != "ADMIN" and (
        not can_bo or lop_hoc_phan.ma_can_bo != can_bo.ma_can_bo
    ):
        raise PermissionDeniedError("Khong co quyen thao tac tren lop hoc phan nay")
    return lop_hoc_phan


def ensure_can_manage_buoi_hoc(
    *,
    session: Session,
    current_account: Any,
    buoi_hoc: Any,
) -> Any:
    return ensure_can_manage_lop_hoc_phan(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=buoi_hoc.ma_lop_hoc_phan,
    )


# Lesson Service Methods
def list_lessons(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Return paginated lessons list."""
    from app.crud import buoihoc_crud
    return buoihoc_crud.get_buoihocs(session=session, skip=skip, limit=limit)


def list_lessons_by_lop_hoc_phan(
    *,
    session: Session,
    current_account: Any,
    ma_lop_hoc_phan: int,
) -> list[Any]:
    """Return lessons for a specific class section."""
    from app.models import BuoiHoc
    from sqlmodel import select

    # Validate access
    ensure_can_manage_lop_hoc_phan(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=ma_lop_hoc_phan,
    )
    statement = select(BuoiHoc).where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan)
    return session.exec(statement).all()


def get_lesson_detail(
    *,
    session: Session,
    current_account: Any,
    ma_buoi_hoc: int,
) -> dict[str, Any]:
    """Return detailed lesson info."""
    from app.crud import buoihoc_crud
    from app.models import LopHocPhan, HocPhan, CanBo
    
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise LessonNotFoundError("Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=item,
    )
    lop_hoc_phan = session.get(LopHocPhan, item.ma_lop_hoc_phan)
    hoc_phan = session.get(HocPhan, lop_hoc_phan.ma_hoc_phan) if lop_hoc_phan else None
    can_bo = session.get(CanBo, lop_hoc_phan.ma_can_bo) if lop_hoc_phan else None

    result = item.model_dump()
    result["ma_buoi_hoc"] = item.ma_buoi_hoc
    result["ten_hoc_phan"] = hoc_phan.ten_hoc_phan if hoc_phan else "N/A"
    result["ten_giang_vien"] = f"{can_bo.ho} {can_bo.ten}".strip() if can_bo else "N/A"
    return result


def create_lesson(
    *,
    session: Session,
    current_account: Any,
    item_in: Any,
) -> Any:
    """Create a lesson."""
    from app.crud import buoihoc_crud

    ensure_can_manage_lop_hoc_phan(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=item_in.ma_lop_hoc_phan,
    )
    if not item_in.trang_thai:
        item_in.trang_thai = "CHUA_DIEM_DANH"
    return buoihoc_crud.create_buoihoc(session=session, item_create=item_in)


def update_lesson(
    *,
    session: Session,
    current_account: Any,
    ma_buoi_hoc: int,
    item_in: Any,
) -> Any:
    """Update a lesson."""
    from app.crud import buoihoc_crud

    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise LessonNotFoundError("Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=item,
    )
    if item_in.ma_lop_hoc_phan and item_in.ma_lop_hoc_phan != item.ma_lop_hoc_phan:
        ensure_can_manage_lop_hoc_phan(
            session=session,
            current_account=current_account,
            ma_lop_hoc_phan=item_in.ma_lop_hoc_phan,
        )
    return buoihoc_crud.update_buoihoc(session=session, db_item=item, item_update=item_in)


def delete_lesson(
    *,
    session: Session,
    ma_buoi_hoc: int,
) -> Message:
    """Delete a lesson."""
    from app.crud import buoihoc_crud

    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise LessonNotFoundError("Buoi hoc khong ton tai")
    buoihoc_crud.delete_buoihoc(session=session, db_item=item)
    return Message(message="Xoa buoi hoc thanh cong")


def open_attendance(
    *,
    session: Session,
    current_account: Any,
    ma_buoi_hoc: int,
) -> Any:
    """Open attendance for a lesson."""
    from app.crud import buoihoc_crud

    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise LessonNotFoundError("Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=item,
    )
    if item.trang_thai == "DA_HUY":
        raise LessonClosedError()

    item.trang_thai = "DANG_DIEN_RA"
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def close_attendance(
    *,
    session: Session,
    current_account: Any,
    ma_buoi_hoc: int,
) -> Any:
    """Close attendance for a lesson."""
    from app.crud import buoihoc_crud, diemdanh_crud

    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise LessonNotFoundError("Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=item,
    )
    if item.trang_thai != "DANG_DIEN_RA":
        raise AppException("Buoi hoc chua duoc mo diem danh hoac da ket thuc", status_code=400)

    item.trang_thai = "DA_KET_THUC"
    session.add(item)
    session.commit()
    session.refresh(item)
    diemdanh_crud.finalize_absent_attendance(session=session, buoi_hoc=item)
    return item


def cancel_lesson_by_giangvien(
    *,
    session: Session,
    current_account: Any,
    ma_buoi_hoc: int,
) -> Any:
    """Cancel a lesson by a teacher/lecturer."""
    from app.crud import buoihoc_crud

    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise LessonNotFoundError("Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=item,
    )
    if item.trang_thai == "DA_KET_THUC":
        raise LessonCompletedError()

    item.trang_thai = "DA_HUY"
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_lesson_attendance_list(
    *,
    session: Session,
    current_account: Any,
    ma_buoi_hoc: int,
) -> list[dict[str, Any]]:
    """Return attendance list for a lesson."""
    from app.models import BuoiHoc, SinhVien, DangKyHocPhan, DiemDanh, AnhDiemDanh
    from sqlmodel import select

    buoi_hoc = session.get(BuoiHoc, ma_buoi_hoc)
    if not buoi_hoc:
        raise LessonNotFoundError("Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=buoi_hoc,
    )

    statement_sv = (
        select(SinhVien)
        .join(DangKyHocPhan, DangKyHocPhan.ma_sinh_vien == SinhVien.ma_sinh_vien)
        .where(DangKyHocPhan.ma_lop_hoc_phan == buoi_hoc.ma_lop_hoc_phan)
    )
    sinh_viens = session.exec(statement_sv).all()

    statement_dd = select(DiemDanh).where(DiemDanh.ma_buoi_hoc == ma_buoi_hoc)
    diem_danhs = session.exec(statement_dd).all()
    dd_map = {dd.ma_sinh_vien: dd for dd in diem_danhs}

    result = []
    for sv in sinh_viens:
        dd = dd_map.get(sv.ma_sinh_vien)
        trang_thai = dd.trang_thai if dd else "CHUA_DIEM_DANH"
        ghi_chu = dd.ghi_chu if dd else None
        
        # Check if attendance proof image exists
        evidence_path = None
        if dd:
            statement_evidence = (
                select(AnhDiemDanh)
                .where(AnhDiemDanh.ma_diem_danh == dd.ma_diem_danh)
                .order_by(AnhDiemDanh.ngay_tao.desc())
            )
            evidence = session.exec(statement_evidence).first()
            evidence_path = evidence.duong_dan_anh if evidence else None

        result.append({
            "ma_sinh_vien": sv.ma_sinh_vien,
            "ho": sv.ho,
            "ten": sv.ten,
            "ma_lop_hoc_phan": buoi_hoc.ma_lop_hoc_phan,
            "trang_thai": trang_thai,
            "ghi_chu": ghi_chu,
            "anh_minh_chung": evidence_path
        })
    return result

