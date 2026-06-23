from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import DangKyHocPhan, DangKyHocPhanCreate, DangKyHocPhanUpdate, DangKyHocPhanPublic, DangKyHocPhansPublic
from app.crud import dangkyhocphan_crud

router = APIRouter(prefix="/dangkyhocphan", tags=["dangkyhocphan"])

@router.get("/", response_model=DangKyHocPhansPublic)
def read_dangkyhocphans(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    items, count = dangkyhocphan_crud.get_dangkyhocphans(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}

@router.get("/{ma_dang_ky}", response_model=DangKyHocPhanPublic)
def read_dangkyhocphan(session: SessionDep, ma_dang_ky: int) -> Any:
    item = dangkyhocphan_crud.get_dangkyhocphan(session=session, ma_dang_ky=ma_dang_ky)
    if not item:
        raise HTTPException(status_code=404, detail="DangKyHocPhan not found")
    return item

@router.post("/", response_model=DangKyHocPhanPublic, dependencies=[Depends(get_current_active_superuser)])
def create_dangkyhocphan(session: SessionDep, item_in: DangKyHocPhanCreate) -> Any:
    item = dangkyhocphan_crud.create_dangkyhocphan(session=session, item_create=item_in)
    return item

@router.patch("/{ma_dang_ky}", response_model=DangKyHocPhanPublic, dependencies=[Depends(get_current_active_superuser)])
def update_dangkyhocphan(session: SessionDep, ma_dang_ky: int, item_in: DangKyHocPhanUpdate) -> Any:
    item = dangkyhocphan_crud.get_dangkyhocphan(session=session, ma_dang_ky=ma_dang_ky)
    if not item:
        raise HTTPException(status_code=404, detail="DangKyHocPhan not found")
    item = dangkyhocphan_crud.update_dangkyhocphan(session=session, db_item=item, item_update=item_in)
    return item

@router.delete("/{ma_dang_ky}", dependencies=[Depends(get_current_active_superuser)])
def delete_dangkyhocphan(session: SessionDep, ma_dang_ky: int) -> Any:
    item = dangkyhocphan_crud.get_dangkyhocphan(session=session, ma_dang_ky=ma_dang_ky)
    if not item:
        raise HTTPException(status_code=404, detail="DangKyHocPhan not found")
    dangkyhocphan_crud.delete_dangkyhocphan(session=session, db_item=item)
    return {"message": "DangKyHocPhan deleted successfully"}
