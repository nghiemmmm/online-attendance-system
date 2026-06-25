"""
Sinh vien router.

Defines APIs for managing student profiles.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Message,
    Nganh,
    SinhVienCreate,
    SinhVienPublic,
    SinhViensPublic,
    SinhVienUpdate,
    LopHocPhan,
    BuoiHoc,
    DiemDanh,
    DangKyHocPhan,
)

from app.api.deps import get_current_active_sinhvien, CurrentAccount
from app.services.canhbaohoc_tap_service import get_canh_bao_vang_by_sinh_vien


router = APIRouter(prefix="/sinh-vien", tags=["sinh-vien"])


def ensure_nganh_exists(*, session: SessionDep, ma_nganh: int | None) -> None:
    """Kiem tra nganh ton tai truoc khi tao hoac cap nhat sinh vien."""
    if ma_nganh is None:
        return
    if not session.get(Nganh, ma_nganh):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Major not found",
        )


def ensure_unique_sinh_vien_fields(
    *,
    session: SessionDep,
    google_email: str | None = None,
    ma_tai_khoan: int | None = None,
    current_ma_sinh_vien: int | None = None,
) -> None:
    """Kiem tra Google email va tai khoan lien ket khong bi trung."""
    if google_email:
        existing_sinh_vien = crud.get_sinh_vien_by_google_email(
            session=session,
            google_email=google_email,
        )
        if (
            existing_sinh_vien
            and existing_sinh_vien.ma_sinh_vien != current_ma_sinh_vien
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Google email already exists",
            )

    if ma_tai_khoan:
        existing_sinh_vien = crud.get_sinh_vien_by_account_id(
            session=session,
            ma_tai_khoan=ma_tai_khoan,
        )
        if (
            existing_sinh_vien
            and existing_sinh_vien.ma_sinh_vien != current_ma_sinh_vien
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account is already linked to another student profile",
            )


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SinhViensPublic,
)
def read_sinh_viens(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    q: Annotated[str | None, Query(max_length=100)] = None,
    ma_nganh: Annotated[int | None, Query(ge=1)] = None,
    trang_thai_hoc: bool | None = None,
) -> SinhViensPublic:
    """Lay danh sach sinh vien, ho tro phan trang, tim kiem va loc."""
    sinh_viens, count = crud.get_sinh_viens(
        session=session,
        skip=skip,
        limit=limit,
        q=q,
        ma_nganh=ma_nganh,
        trang_thai_hoc=trang_thai_hoc,
    )
    return SinhViensPublic(data=sinh_viens, count=count)


@router.get(
    "/me/lich-hoc",
    dependencies=[Depends(get_current_active_sinhvien)],
)
def get_my_lich_hoc(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem lịch học của mình."""
    sinh_vien = crud.get_sinh_vien_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not sinh_vien:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ sinh viên")
    
    # Tìm các lớp học phần sinh viên đăng ký
    from app.models.hocphan import HocPhan
    from datetime import date
    statement = (
        select(LopHocPhan, BuoiHoc, HocPhan)
        .join(DangKyHocPhan, DangKyHocPhan.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .join(BuoiHoc, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan)
        .where(DangKyHocPhan.ma_sinh_vien == sinh_vien.ma_sinh_vien)
        .where(BuoiHoc.ngay_hoc >= date.today())
        .where(BuoiHoc.trang_thai != "DA_KET_THUC")
        .where(BuoiHoc.trang_thai != "DA_HUY")
        .order_by(BuoiHoc.ngay_hoc.asc(), BuoiHoc.gio_bat_dau.asc())
    )
    results = session.exec(statement).all()
    
    # Format lại kết quả
    lich_hoc = []
    for lhp, bh, hp in results:
        lich_hoc.append({
            "ma_buoi_hoc": bh.ma_buoi_hoc,
            "ma_lop_hoc_phan": lhp.ma_lop_hoc_phan,
            "ma_hoc_phan": lhp.ma_hoc_phan,
            "ten_hoc_phan": hp.ten_hoc_phan,
            "ngay_hoc": bh.ngay_hoc,
            "gio_bat_dau": bh.gio_bat_dau,
            "gio_ket_thuc": bh.gio_ket_thuc,
            "trang_thai": bh.trang_thai
        })
    return {"data": lich_hoc, "count": len(lich_hoc)}


@router.get(
    "/me/diem-danh",
    dependencies=[Depends(get_current_active_sinhvien)],
)
def get_my_diem_danh(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem lịch sử điểm danh."""
    sinh_vien = crud.get_sinh_vien_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not sinh_vien:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ sinh viên")
    
    from app.models.hocphan import HocPhan
    statement = (
        select(DiemDanh, BuoiHoc, LopHocPhan, HocPhan)
        .join(BuoiHoc, BuoiHoc.ma_buoi_hoc == DiemDanh.ma_buoi_hoc)
        .join(LopHocPhan, LopHocPhan.ma_lop_hoc_phan == BuoiHoc.ma_lop_hoc_phan)
        .join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan)
        .where(DiemDanh.ma_sinh_vien == sinh_vien.ma_sinh_vien)
    )
    results = session.exec(statement).all()
    
    lich_su = []
    for dd, bh, lhp, hp in results:
        lich_su.append({
            "ma_diem_danh": dd.ma_diem_danh,
            "ma_lop_hoc_phan": lhp.ma_lop_hoc_phan,
            "ten_hoc_phan": hp.ten_hoc_phan,
            "ngay_hoc": bh.ngay_hoc,
            "trang_thai": dd.trang_thai,
            "thoi_diem_diem_danh": dd.thoi_diem_diem_danh,
            "ghi_chu": dd.ly_do_chinh_sua
        })
    return {"data": lich_su, "count": len(lich_su)}


@router.get(
    "/me/canh-bao",
    dependencies=[Depends(get_current_active_sinhvien)],
)
def get_my_canh_bao(session: SessionDep, current_account: CurrentAccount) -> Any:
    """Sinh viên xem các cảnh báo vắng mặt."""
    sinh_vien = crud.get_sinh_vien_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not sinh_vien:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ sinh viên")
    
    return get_canh_bao_vang_by_sinh_vien(
        session=session,
        ma_sinh_vien=sinh_vien.ma_sinh_vien,
        warning_threshold=15.0,
        absence_limit=20.0,
        include_safe=True,
    )


@router.get(
    "/{ma_sinh_vien}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SinhVienPublic,
)
def read_sinh_vien(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
) -> SinhVienPublic:
    """Lay chi tiet mot sinh vien theo ma sinh vien."""
    sinh_vien = crud.get_sinh_vien(session=session, ma_sinh_vien=ma_sinh_vien)
    if not sinh_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return sinh_vien


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SinhVienPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_sinh_vien(
    *,
    session: SessionDep,
    sinh_vien_in: SinhVienCreate,
) -> SinhVienPublic:
    """Tao ho so sinh vien moi."""
    ensure_nganh_exists(session=session, ma_nganh=sinh_vien_in.ma_nganh)
    ensure_unique_sinh_vien_fields(
        session=session,
        google_email=sinh_vien_in.google_email,
        ma_tai_khoan=sinh_vien_in.ma_tai_khoan,
    )
    try:
        return crud.create_sinh_vien(
            session=session,
            sinh_vien_create=sinh_vien_in,
        )
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student profile violates a unique or foreign key constraint",
        ) from exc


@router.patch(
    "/{ma_sinh_vien}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=SinhVienPublic,
)
def update_sinh_vien(
    *,
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
    sinh_vien_in: SinhVienUpdate,
) -> SinhVienPublic:
    """Cap nhat mot phan thong tin sinh vien."""
    db_sinh_vien = crud.get_sinh_vien(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
    )
    if not db_sinh_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    ensure_nganh_exists(session=session, ma_nganh=sinh_vien_in.ma_nganh)
    ensure_unique_sinh_vien_fields(
        session=session,
        google_email=sinh_vien_in.google_email,
        ma_tai_khoan=sinh_vien_in.ma_tai_khoan,
        current_ma_sinh_vien=ma_sinh_vien,
    )
    try:
        return crud.update_sinh_vien(
            session=session,
            db_sinh_vien=db_sinh_vien,
            sinh_vien_update=sinh_vien_in,
        )
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student profile violates a unique or foreign key constraint",
        ) from exc


@router.delete(
    "/{ma_sinh_vien}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_sinh_vien(
    session: SessionDep,
    ma_sinh_vien: Annotated[int, Path(ge=1)],
) -> Message:
    """Xoa ho so sinh vien theo ma sinh vien."""
    db_sinh_vien = crud.get_sinh_vien(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
    )
    if not db_sinh_vien:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    try:
        crud.delete_sinh_vien(session=session, db_sinh_vien=db_sinh_vien)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student profile is referenced by other records",
        ) from exc

    return Message(message="Student profile deleted successfully")


@router.get(
    "/me/lop-hoc-phan-available",
    dependencies=[Depends(get_current_active_sinhvien)],
)
def get_available_lop_hoc_phan(
    session: SessionDep,
    current_account: CurrentAccount,
    hoc_ky: int = 1,
    nam_hoc: str = "2025-2026",
) -> Any:
    """Lấy danh sách lớp học phần có sẵn và đánh dấu xem sinh viên hiện tại đã đăng ký chưa."""
    sinh_vien = crud.get_sinh_vien_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not sinh_vien:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ sinh viên")
    
    from app.models.hocphan import HocPhan
    from app.models.canbo import CanBo
    
    statement = (
        select(LopHocPhan, HocPhan, CanBo)
        .join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan)
        .join(CanBo, CanBo.ma_can_bo == LopHocPhan.ma_can_bo)
        .where(
            LopHocPhan.trang_thai == True,
            LopHocPhan.hoc_ky == hoc_ky,
            LopHocPhan.nam_hoc == nam_hoc,
        )
    )
    results = session.exec(statement).all()
    
    registered_statement = (
        select(DangKyHocPhan.ma_lop_hoc_phan)
        .where(DangKyHocPhan.ma_sinh_vien == sinh_vien.ma_sinh_vien)
    )
    registered_class_ids = set(session.exec(registered_statement).all())
    
    available_classes = []
    for lhp, hp, cb in results:
        available_classes.append({
            "ma_lop_hoc_phan": lhp.ma_lop_hoc_phan,
            "ma_hoc_phan": lhp.ma_hoc_phan,
            "ten_hoc_phan": hp.ten_hoc_phan,
            "so_tin_chi": hp.so_tin_chi,
            "ten_giang_vien": f"{cb.ho} {cb.ten}".strip(),
            "hoc_ky": lhp.hoc_ky,
            "nam_hoc": lhp.nam_hoc,
            "ty_le_chuyen_can_toi_thieu": lhp.ty_le_chuyen_can_toi_thieu,
            "is_registered": lhp.ma_lop_hoc_phan in registered_class_ids
        })
        
    return {"data": available_classes, "count": len(available_classes)}


@router.post(
    "/me/dang-ky-hoc-phan",
    dependencies=[Depends(get_current_active_sinhvien)],
)
def register_my_lop_hoc_phan(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Sinh viên tự đăng ký lớp học phần."""
    sinh_vien = crud.get_sinh_vien_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not sinh_vien:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ sinh viên")
        
    existing = session.exec(
        select(DangKyHocPhan)
        .where(DangKyHocPhan.ma_sinh_vien == sinh_vien.ma_sinh_vien)
        .where(DangKyHocPhan.ma_lop_hoc_phan == ma_lop_hoc_phan)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bạn đã đăng ký lớp học phần này rồi")
        
    lhp = session.get(LopHocPhan, ma_lop_hoc_phan)
    if not lhp:
        raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")
        
    reg = DangKyHocPhan(
        ma_sinh_vien=sinh_vien.ma_sinh_vien,
        ma_lop_hoc_phan=ma_lop_hoc_phan
    )
    session.add(reg)
    
    import random
    buoihocs = session.exec(
        select(BuoiHoc).where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan)
    ).all()
    
    statuses = ["CO_MAT", "DI_MUON", "VANG"]
    methods = ["KHUON_MAT", "THU_CONG"]
    
    for idx, bh in enumerate(buoihocs):
        status = statuses[idx % len(statuses)]
        method = methods[idx % len(methods)]
        confidence = round(random.uniform(0.85, 0.99), 2) if method == "KHUON_MAT" else None
        
        dd = DiemDanh(
            ma_sinh_vien=sinh_vien.ma_sinh_vien,
            ma_buoi_hoc=bh.ma_buoi_hoc,
            trang_thai=status,
            phuong_thuc=method,
            do_tin_cay=confidence
        )
        session.add(dd)
        
    session.commit()
    return {"message": "Đăng ký học phần thành công"}


@router.delete(
    "/me/huy-dang-ky-hoc-phan/{ma_lop_hoc_phan}",
    dependencies=[Depends(get_current_active_sinhvien)],
)
def cancel_my_lop_hoc_phan(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Sinh viên tự hủy đăng ký lớp học phần."""
    sinh_vien = crud.get_sinh_vien_by_account_id(session=session, ma_tai_khoan=current_account.ma_tai_khoan)
    if not sinh_vien:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ sinh viên")
        
    reg = session.exec(
        select(DangKyHocPhan)
        .where(DangKyHocPhan.ma_sinh_vien == sinh_vien.ma_sinh_vien)
        .where(DangKyHocPhan.ma_lop_hoc_phan == ma_lop_hoc_phan)
    ).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi đăng ký học phần")
        
    session.delete(reg)
    
    buoi_hoc_ids_statement = select(BuoiHoc.ma_buoi_hoc).where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan)
    buoi_hoc_ids = session.exec(buoi_hoc_ids_statement).all()
    
    if buoi_hoc_ids:
        diem_danh_records = session.exec(
            select(DiemDanh)
            .where(DiemDanh.ma_sinh_vien == sinh_vien.ma_sinh_vien)
            .where(DiemDanh.ma_buoi_hoc.in_(buoi_hoc_ids))
        ).all()
        for dd in diem_danh_records:
            from sqlalchemy import text
            session.execute(text("DELETE FROM khieunai WHERE ma_diem_danh = :dd_id"), {"dd_id": dd.ma_diem_danh})
            session.delete(dd)
            
    session.commit()
    return {"message": "Hủy đăng ký học phần thành công"}
