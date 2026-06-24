from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    BuoiHocGanDaysPublic,
    CanBoCreate,
    CanBoPublic,
    CanBosPublic,
    CanBoUpdate,
    LichDaysPublic,
    Message,
    MonthlyAttendanceSummary,
    KhieuNaiChoXuLyMetric,
    SoLuongLopHocPhanDangDayPublic,
)
from app.services.attendance_summary_service import get_monthly_attendance_summary
from app.services.khieunai_service import get_khieu_nai_cho_xu_ly_metric

router = APIRouter(prefix="/canbo", tags=["canbo"])


def ensure_unique_can_bo_fields(
    *,
    session: SessionDep,
    google_email: str | None = None,
    ma_tai_khoan: int | None = None,
    current_ma_can_bo: int | None = None,
) -> None:
    """
    Kiểm tra Google email và tài khoản liên kết không bị trùng với cán bộ khác.

    Hàm dùng cho cả tạo mới và cập nhật để tránh lỗi unique constraint từ database.
    """
    if google_email:
        existing_can_bo = crud.get_can_bo_by_google_email(
            session=session,
            google_email=google_email,
        )
        if (
            existing_can_bo
            and existing_can_bo.ma_can_bo != current_ma_can_bo
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Google email already exists",
            )

    if ma_tai_khoan:
        existing_can_bo = crud.get_can_bo_by_account_id(
            session=session,
            ma_tai_khoan=ma_tai_khoan,
        )
        if (
            existing_can_bo
            and existing_can_bo.ma_can_bo != current_ma_can_bo
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account is already linked to another staff profile",
            )


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanBosPublic,
)
def read_can_bos(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    q: Annotated[str | None, Query(max_length=100)] = None,
    trang_thai: bool | None = None,
) -> CanBosPublic:
    """
    Lấy danh sách cán bộ.

    Hỗ trợ phân trang, tìm kiếm theo họ/tên/email/chức vụ và lọc theo trạng thái.
    """
    can_bos, count = crud.get_can_bos(
        session=session,
        skip=skip,
        limit=limit,
        q=q,
        trang_thai=trang_thai,
    )
    return CanBosPublic(data=can_bos, count=count)


@router.get(
    "/{ma_can_bo}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanBoPublic,
)
def read_can_bo(
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
) -> CanBoPublic:
    """Lấy chi tiết một cán bộ theo mã cán bộ."""
    can_bo = crud.get_can_bo(session=session, ma_can_bo=ma_can_bo)
    if not can_bo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found",
        )
    return can_bo


from app.api.deps import SessionDep, get_current_active_superuser, get_current_active_giangvien, CurrentAccount
from sqlmodel import select
from app.models import LopHocPhan, HocPhan

@router.get(
    "/me/lich-day",
    dependencies=[Depends(get_current_active_giangvien)],
)
def read_my_lich_day(
    session: SessionDep,
    current_account: CurrentAccount,
    from_date: date | None = None,
    to_date: date | None = None,
    hoc_ky: Annotated[int | None, Query(ge=1, le=3)] = None,
    nam_hoc: Annotated[str | None, Query(max_length=20)] = None,
    trang_thai: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> Any:
    """Lấy lịch dạy của cán bộ đang đăng nhập."""
    can_bo = crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not can_bo:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ cán bộ")
    
    lich_day, count = crud.get_lich_day_by_can_bo(
        session=session, ma_can_bo=can_bo.ma_can_bo, from_date=from_date, to_date=to_date, hoc_ky=hoc_ky, nam_hoc=nam_hoc, trang_thai=trang_thai, skip=skip, limit=limit,
    )
    return {"data": lich_day, "count": count}

@router.get(
    "/me/lop-hoc-phan",
    dependencies=[Depends(get_current_active_giangvien)],
)
def read_my_lop_hoc_phan(
    session: SessionDep,
    current_account: CurrentAccount,
) -> Any:
    """Lấy danh sách các lớp học phần cán bộ đang giảng dạy."""
    can_bo = crud.get_can_bo_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not can_bo:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ cán bộ")
    
    statement = select(LopHocPhan, HocPhan).join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan).where(LopHocPhan.ma_can_bo == can_bo.ma_can_bo)
    results = session.exec(statement).all()
    
    lop_hoc_phans = []
    for lhp, hp in results:
        reg_count = session.exec(
            select(func.count(DangKyHocPhan.ma_sinh_vien))
            .where(DangKyHocPhan.ma_lop_hoc_phan == lhp.ma_lop_hoc_phan)
        ).first() or 0
        
        lop_hoc_phans.append({
            "ma_lop_hoc_phan": lhp.ma_lop_hoc_phan,
            "ma_hoc_phan": lhp.ma_hoc_phan,
            "ten_hoc_phan": hp.ten_hoc_phan,
            "hoc_ky": lhp.hoc_ky,
            "nam_hoc": lhp.nam_hoc,
            "trang_thai": lhp.trang_thai,
            "si_so_hien_tai": reg_count
        })
    return {"data": lop_hoc_phans, "count": len(lop_hoc_phans)}


@router.get(
    "/{ma_can_bo}/lich-day",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=LichDaysPublic,
)
def read_lich_day_can_bo(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    from_date: date | None = None,
    to_date: date | None = None,
    hoc_ky: Annotated[int | None, Query(ge=1, le=3)] = None,
    nam_hoc: Annotated[str | None, Query(max_length=20)] = None,
    trang_thai: bool | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> LichDaysPublic:
    """Lấy lịch dạy của một cán bộ/giảng viên."""
    if from_date and to_date and from_date > to_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="from_date must be before or equal to to_date")
    can_bo = crud.get_can_bo(session=session, ma_can_bo=ma_can_bo)
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")
    lich_day, count = crud.get_lich_day_by_can_bo(
        session=session, ma_can_bo=ma_can_bo, from_date=from_date, to_date=to_date, hoc_ky=hoc_ky, nam_hoc=nam_hoc, trang_thai=trang_thai, skip=skip, limit=limit,
    )
    return LichDaysPublic(data=lich_day, count=count)

@router.get(
    "/{ma_can_bo}/buoi-hoc/gan-day",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=BuoiHocGanDaysPublic,
)
def read_buoi_hoc_gan_day_can_bo(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> BuoiHocGanDaysPublic:
    """Lay danh sach buoi hoc gan day cua can bo kem thong ke diem danh."""
    can_bo = crud.get_can_bo(session=session, ma_can_bo=ma_can_bo)
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")
    buoi_hocs, count = crud.get_buoi_hoc_gan_day_by_can_bo(session=session, ma_can_bo=ma_can_bo, limit=limit)
    return BuoiHocGanDaysPublic(data=buoi_hocs, count=count)

@router.get(
    "/{ma_can_bo}/lop-hoc-phan/dang-day/count",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=SoLuongLopHocPhanDangDayPublic,
)
def count_lop_hoc_phan_dang_day(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    as_of_date: date | None = None,
) -> SoLuongLopHocPhanDangDayPublic:
    can_bo = crud.get_can_bo(session=session, ma_can_bo=ma_can_bo)
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")
    target_date = as_of_date or date.today()
    count, hoc_ky, nam_hoc = crud.count_lop_hoc_phan_dang_day_by_can_bo(session=session, ma_can_bo=ma_can_bo, as_of_date=target_date)
    return SoLuongLopHocPhanDangDayPublic(ma_can_bo=ma_can_bo, hoc_ky=hoc_ky, nam_hoc=nam_hoc, as_of_date=target_date, count=count)

@router.get(
    "/{ma_can_bo}/attendance/monthly-summary",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=MonthlyAttendanceSummary,
)
def read_monthly_attendance_summary(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    reference_date: date | None = None,
) -> MonthlyAttendanceSummary:
    can_bo = crud.get_can_bo(session=session, ma_can_bo=ma_can_bo)
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")
    return get_monthly_attendance_summary(session=session, ma_can_bo=ma_can_bo, reference_date=reference_date or date.today())

@router.get(
    "/{ma_can_bo}/khieu-nai/cho-xu-ly/count",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=KhieuNaiChoXuLyMetric,
)
def read_khieu_nai_cho_xu_ly_count(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
) -> KhieuNaiChoXuLyMetric:
    can_bo = crud.get_can_bo(session=session, ma_can_bo=ma_can_bo)
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")
    return get_khieu_nai_cho_xu_ly_metric(session=session, ma_can_bo=ma_can_bo)

@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanBoPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_can_bo(
    *,
    session: SessionDep,
    can_bo_in: CanBoCreate,
) -> CanBoPublic:
    """Tạo hồ sơ cán bộ mới."""
    ensure_unique_can_bo_fields(
        session=session,
        google_email=can_bo_in.google_email,
        ma_tai_khoan=can_bo_in.ma_tai_khoan,
    )
    try:
        return crud.create_can_bo(session=session, can_bo_create=can_bo_in)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Staff profile violates a unique or foreign key constraint",
        ) from exc


@router.patch(
    "/{ma_can_bo}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=CanBoPublic,
)
def update_can_bo(
    *,
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
    can_bo_in: CanBoUpdate,
) -> CanBoPublic:
    """Cập nhật một phần thông tin cán bộ."""
    db_can_bo = crud.get_can_bo(session=session, ma_can_bo=ma_can_bo)
    if not db_can_bo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found",
        )

    ensure_unique_can_bo_fields(
        session=session,
        google_email=can_bo_in.google_email,
        ma_tai_khoan=can_bo_in.ma_tai_khoan,
        current_ma_can_bo=ma_can_bo,
    )
    try:
        return crud.update_can_bo(
            session=session,
            db_can_bo=db_can_bo,
            can_bo_update=can_bo_in,
        )
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Staff profile violates a unique or foreign key constraint",
        ) from exc


@router.delete(
    "/{ma_can_bo}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_can_bo(
    session: SessionDep,
    ma_can_bo: Annotated[int, Path(ge=1)],
) -> Message:
    """Xóa hồ sơ cán bộ theo mã cán bộ."""
    db_can_bo = crud.get_can_bo(session=session, ma_can_bo=ma_can_bo)
    if not db_can_bo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found",
        )
    try:
        crud.delete_can_bo(session=session, db_can_bo=db_can_bo)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Staff profile is referenced by other records",
        ) from exc

    return Message(message="Staff profile deleted successfully")
