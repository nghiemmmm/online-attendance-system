"""
Khieu nai router.

Defines APIs for staff members to view and process pending attendance complaints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.api.deps import SessionDep, get_current_active_superuser, CurrentAccount, get_current_active_sinhvien
from fastapi import APIRouter, Depends, Path, Query, HTTPException
from sqlmodel import select, func, col
from datetime import datetime, timedelta

from app.models import (

    KhieuNai,
    KhieuNaiCreate,
    KhieuNaiPublic,
    KhieuNaisPublic,
    KhieuNaiCanXuLyDetail,
    KhieuNaiCanXuLysPublic,
    KhieuNaiChapThuanRequest,
    KhieuNaiXuLyRequest,
    KhieuNaiXuLyResult,
    SinhVien,
    CanBo,
)
from app.services.khieunai_service import (
    chap_thuan_khieu_nai,
    get_khieu_nai_can_xu_ly_detail,
    list_khieu_nai_can_xu_ly,
    tu_choi_khieu_nai,
)

router = APIRouter(prefix="/khieu-nai", tags=["khieu-nai"])

@router.post(
    "",
    dependencies=[Depends(get_current_active_sinhvien)],
    response_model=KhieuNaiPublic,
)
def create_khieu_nai(
    session: SessionDep,
    payload: KhieuNaiCreate,
    current_account: CurrentAccount,
) -> KhieuNaiPublic:
    # Ensure student is submitting claim for themselves
    sinh_vien = session.exec(select(SinhVien).where(SinhVien.ma_tai_khoan == current_account.ma_tai_khoan)).first()
    if not sinh_vien:
        raise HTTPException(status_code=403, detail="Not a student")
    if payload.ma_sinh_vien != sinh_vien.ma_sinh_vien:
        raise HTTPException(status_code=403, detail="Cannot submit claim for another student")

    # Kiểm tra đã có khiếu nại cho bản ghi này chưa
    existing_khieu_nai = session.exec(select(KhieuNai).where(KhieuNai.ma_diem_danh == payload.ma_diem_danh)).first()
    if existing_khieu_nai:
        raise HTTPException(status_code=400, detail="Đã tồn tại khiếu nại cho bản ghi điểm danh này")

    # Kiểm tra giới hạn 48 giờ
    from app.models import DiemDanh, BuoiHoc
    diem_danh = session.get(DiemDanh, payload.ma_diem_danh)
    if not diem_danh:
        raise HTTPException(status_code=404, detail="Bản ghi điểm danh không tồn tại")
    
    buoi_hoc = session.get(BuoiHoc, diem_danh.ma_buoi_hoc)
    if not buoi_hoc:
        raise HTTPException(status_code=404, detail="Buổi học không tồn tại")
        
    if buoi_hoc.gio_ket_thuc:
        # Nếu có giờ kết thúc thì tính từ thời điểm đó
        thoi_gian_ket_thuc = datetime.combine(buoi_hoc.ngay_hoc, buoi_hoc.gio_ket_thuc)
    else:
        # Nếu không có giờ kết thúc thì mặc định là cuối ngày học
        thoi_gian_ket_thuc = datetime.combine(buoi_hoc.ngay_hoc, datetime.max.time())
        
    if datetime.now() > thoi_gian_ket_thuc + timedelta(hours=48):
        raise HTTPException(status_code=400, detail="Đã quá thời hạn 48 giờ để gửi khiếu nại cho buổi học này")

    db_khieu_nai = KhieuNai.model_validate(payload)
    session.add(db_khieu_nai)
    session.commit()
    session.refresh(db_khieu_nai)
    return db_khieu_nai


@router.get(
    "",
    dependencies=[Depends(get_current_active_sinhvien)],
    response_model=KhieuNaisPublic,
)
def read_my_khieu_nai(
    session: SessionDep,
    current_account: CurrentAccount,
    skip: int = 0,
    limit: int = 100,
) -> KhieuNaisPublic:
    sinh_vien = session.exec(select(SinhVien).where(SinhVien.ma_tai_khoan == current_account.ma_tai_khoan)).first()
    if not sinh_vien:
        raise HTTPException(status_code=403, detail="Not a student")

    count_statement = select(func.count()).select_from(KhieuNai).where(KhieuNai.ma_sinh_vien == sinh_vien.ma_sinh_vien)
    count = session.exec(count_statement).one()

    statement = (
        select(KhieuNai)
        .where(KhieuNai.ma_sinh_vien == sinh_vien.ma_sinh_vien)
        .order_by(col(KhieuNai.ngay_gui).desc())
        .offset(skip)
        .limit(limit)
    )
    khieu_nais = session.exec(statement).all()
    return KhieuNaisPublic(data=khieu_nais, count=count)




from app.api.deps import get_current_active_giangvien

@router.get(
    "/can-bo/{ma_can_bo}/can-xu-ly",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=KhieuNaiCanXuLysPublic,
)
def read_khieu_nai_can_xu_ly(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> KhieuNaiCanXuLysPublic:
    """Lay danh sach khieu nai can xu ly cua can bo."""
    can_bo = session.exec(select(CanBo).where(CanBo.ma_can_bo == ma_can_bo)).first()
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")

    return list_khieu_nai_can_xu_ly(
        session=session,
        ma_can_bo=ma_can_bo,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=KhieuNaiCanXuLyDetail,
)
def read_khieu_nai_can_xu_ly_detail(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
) -> KhieuNaiCanXuLyDetail:
    """Lay chi tiet mot khieu nai can xu ly cua can bo."""
    can_bo = session.exec(select(CanBo).where(CanBo.ma_can_bo == ma_can_bo)).first()
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")

    return get_khieu_nai_can_xu_ly_detail(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
    )


@router.patch(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}/chap-thuan",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=KhieuNaiXuLyResult,
)
def approve_khieu_nai(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
    payload: KhieuNaiChapThuanRequest,
) -> KhieuNaiXuLyResult:
    """Chap thuan khieu nai va cap nhat diem danh neu co."""
    can_bo = session.exec(select(CanBo).where(CanBo.ma_can_bo == ma_can_bo)).first()
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")
    return chap_thuan_khieu_nai(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
        payload=payload,
    )


@router.patch(
    "/can-bo/{ma_can_bo}/can-xu-ly/{ma_khieu_nai}/tu-choi",
    dependencies=[Depends(get_current_active_giangvien)],
    response_model=KhieuNaiXuLyResult,
)
def reject_khieu_nai(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_can_bo: Annotated[int, Path(ge=1)],
    ma_khieu_nai: Annotated[int, Path(ge=1)],
    payload: KhieuNaiXuLyRequest,
) -> KhieuNaiXuLyResult:
    """Tu choi khieu nai va ghi nhan thong tin xu ly."""
    can_bo = session.exec(select(CanBo).where(CanBo.ma_can_bo == ma_can_bo)).first()
    if not can_bo or can_bo.ma_tai_khoan != current_account.ma_tai_khoan:
        raise HTTPException(status_code=403, detail="Not authorized to access this Can Bo's data")

    return tu_choi_khieu_nai(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_khieu_nai=ma_khieu_nai,
        payload=payload,
    )
