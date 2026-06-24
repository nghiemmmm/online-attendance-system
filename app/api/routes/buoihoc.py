from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_giangvien,
    get_current_active_superuser,
)
from app.crud import buoihoc_crud, canbo_crud, diemdanh_crud
from app.models import (
    BuoiHoc,
    BuoiHocCreate,
    BuoiHocPublic,
    BuoiHocsPublic,
    BuoiHocUpdate,
    CanBo,
    DangKyHocPhan,
    DiemDanh,
    HocPhan,
    LopHocPhan,
    SinhVien,
)

router = APIRouter(prefix="/buoi-hoc", tags=["buoi-hoc"])


def ensure_can_manage_lop_hoc_phan(
    *,
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> LopHocPhan:
    lop_hoc_phan = session.get(LopHocPhan, ma_lop_hoc_phan)
    if not lop_hoc_phan:
        raise HTTPException(status_code=404, detail="Lop hoc phan khong ton tai")

    can_bo = canbo_crud.get_can_bo_by_account_id(
        session=session,
        ma_tai_khoan=current_account.ma_tai_khoan,
    )
    if current_account.vai_tro != "ADMIN" and (
        not can_bo or lop_hoc_phan.ma_can_bo != can_bo.ma_can_bo
    ):
        raise HTTPException(
            status_code=403,
            detail="Khong co quyen thao tac tren lop hoc phan nay",
        )
    return lop_hoc_phan


def ensure_can_manage_buoi_hoc(
    *,
    session: SessionDep,
    current_account: CurrentAccount,
    buoi_hoc: BuoiHoc,
) -> LopHocPhan:
    return ensure_can_manage_lop_hoc_phan(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=buoi_hoc.ma_lop_hoc_phan,
    )


def build_buoi_hoc_detail(session: SessionDep, item: BuoiHoc) -> dict[str, Any]:
    lop_hoc_phan = session.get(LopHocPhan, item.ma_lop_hoc_phan)
    hoc_phan = session.get(HocPhan, lop_hoc_phan.ma_hoc_phan) if lop_hoc_phan else None
    can_bo = session.get(CanBo, lop_hoc_phan.ma_can_bo) if lop_hoc_phan else None

    result = item.model_dump()
    result["ma_buoi_hoc"] = item.ma_buoi_hoc
    result["ten_hoc_phan"] = hoc_phan.ten_hoc_phan if hoc_phan else "N/A"
    result["ten_giang_vien"] = f"{can_bo.ho} {can_bo.ten}".strip() if can_bo else "N/A"
    return result


@router.get("/", response_model=BuoiHocsPublic)
def read_buoihocs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    items, count = buoihoc_crud.get_buoihocs(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}


@router.get(
    "/lop-hoc-phan/{ma_lop_hoc_phan}",
    dependencies=[Depends(get_current_active_giangvien)],
)
def read_buoihocs_by_lop_hoc_phan(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    ensure_can_manage_lop_hoc_phan(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=ma_lop_hoc_phan,
    )
    statement = (
        select(BuoiHoc)
        .where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan)
        .order_by(BuoiHoc.ngay_hoc, BuoiHoc.gio_bat_dau, BuoiHoc.so_buoi)
    )
    items = session.exec(statement).all()
    return {"data": [build_buoi_hoc_detail(session, item) for item in items], "count": len(items)}


@router.get("/{ma_buoi_hoc}", response_model=Any)
def read_buoihoc(
    session: SessionDep,
    ma_buoi_hoc: int,
) -> Any:
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buoi hoc khong ton tai")
    return build_buoi_hoc_detail(session, item)


@router.post(
    "/",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_giangvien)],
)
def create_buoihoc(
    session: SessionDep,
    current_account: CurrentAccount,
    item_in: BuoiHocCreate,
) -> Any:
    ensure_can_manage_lop_hoc_phan(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=item_in.ma_lop_hoc_phan,
    )
    if not item_in.trang_thai:
        item_in.trang_thai = "CHUA_DIEM_DANH"
    return buoihoc_crud.create_buoihoc(session=session, item_create=item_in)


@router.patch(
    "/{ma_buoi_hoc}",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_giangvien)],
)
def update_buoihoc(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
    item_in: BuoiHocUpdate,
) -> Any:
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buoi hoc khong ton tai")

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
    return buoihoc_crud.update_buoihoc(
        session=session,
        db_item=item,
        item_update=item_in,
    )


@router.post(
    "/{ma_buoi_hoc}/mo-diem-danh",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_giangvien)],
)
def mo_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=item,
    )
    if item.trang_thai == "DA_HUY":
        raise HTTPException(status_code=400, detail="Khong the mo buoi hoc da huy")

    item.trang_thai = "DANG_DIEN_RA"
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.post(
    "/{ma_buoi_hoc}/dong-diem-danh",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_giangvien)],
)
def dong_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=item,
    )
    if item.trang_thai != "DANG_DIEN_RA":
        raise HTTPException(
            status_code=400,
            detail="Buoi hoc chua duoc mo diem danh hoac da ket thuc",
        )

    item.trang_thai = "DA_KET_THUC"
    session.add(item)
    session.commit()
    session.refresh(item)
    diemdanh_crud.chot_diem_danh_vang(session=session, buoi_hoc=item)
    return item


@router.delete("/{ma_buoi_hoc}", dependencies=[Depends(get_current_active_superuser)])
def delete_buoihoc(
    session: SessionDep,
    ma_buoi_hoc: int,
) -> Any:
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buoi hoc khong ton tai")
    buoihoc_crud.delete_buoihoc(session=session, db_item=item)
    return {"message": "Xoa buoi hoc thanh cong"}


@router.delete(
    "/{ma_buoi_hoc}/giang-vien",
    response_model=BuoiHocPublic,
    dependencies=[Depends(get_current_active_giangvien)],
)
def cancel_buoihoc_by_giangvien(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    item = buoihoc_crud.get_buoihoc(session=session, ma_buoi_hoc=ma_buoi_hoc)
    if not item:
        raise HTTPException(status_code=404, detail="Buoi hoc khong ton tai")

    ensure_can_manage_buoi_hoc(
        session=session,
        current_account=current_account,
        buoi_hoc=item,
    )
    if item.trang_thai == "DA_KET_THUC":
        raise HTTPException(status_code=400, detail="Khong the huy buoi hoc da ket thuc")

    item.trang_thai = "DA_HUY"
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get(
    "/{ma_buoi_hoc}/diem-danh",
    dependencies=[Depends(get_current_active_giangvien)],
)
def read_buoihoc_diem_danh_list(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_buoi_hoc: int,
) -> Any:
    buoi_hoc = session.get(BuoiHoc, ma_buoi_hoc)
    if not buoi_hoc:
        raise HTTPException(status_code=404, detail="Buoi hoc khong ton tai")

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
    for sinh_vien in sinh_viens:
        diem_danh = dd_map.get(sinh_vien.ma_sinh_vien)
        status = "pending"
        confidence = "medium"
        verified_at = None

        if diem_danh:
            if diem_danh.trang_thai == "CO_MAT":
                status = "present"
            elif diem_danh.trang_thai in {"DI_MUON", "MUON"}:
                status = "late"
            elif diem_danh.trang_thai == "VANG":
                status = "absent"

            if (diem_danh.do_tin_cay or 0) >= 0.85:
                confidence = "high"
            elif (diem_danh.do_tin_cay or 0) >= 0.70:
                confidence = "medium"
            else:
                confidence = "low"
            verified_at = (
                diem_danh.thoi_diem_diem_danh.strftime("%H:%M:%S")
                if diem_danh.thoi_diem_diem_danh
                else None
            )

        result.append(
            {
                "id": str(sinh_vien.ma_sinh_vien),
                "name": f"{sinh_vien.ho} {sinh_vien.ten}".strip(),
                "studentId": f"SV{sinh_vien.ma_sinh_vien:03d}",
                "status": status,
                "confidence": confidence,
                "hasCamera": status != "absent",
                "verifiedAt": verified_at,
            }
        )

    return result
