from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import HocPhan, HocPhanCreate, HocPhanUpdate, HocPhanPublic, HocPhansPublic
from app.crud import hocphan_crud

router = APIRouter(prefix="/hocphan", tags=["hocphan"])

@router.get("/", response_model=HocPhansPublic)
def read_hocphans(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    items, count = hocphan_crud.get_hocphans(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}

@router.get("/{ma_hoc_phan}", response_model=HocPhanPublic)
def read_hocphan(session: SessionDep, ma_hoc_phan: int) -> Any:
    item = hocphan_crud.get_hocphan(session=session, ma_hoc_phan=ma_hoc_phan)
    if not item:
        raise HTTPException(status_code=404, detail="HocPhan not found")
    return item

@router.post("/", response_model=HocPhanPublic, dependencies=[Depends(get_current_active_superuser)])
def create_hocphan(session: SessionDep, item_in: HocPhanCreate) -> Any:
    item = hocphan_crud.create_hocphan(session=session, item_create=item_in)
    return item

@router.patch("/{ma_hoc_phan}", response_model=HocPhanPublic, dependencies=[Depends(get_current_active_superuser)])
def update_hocphan(session: SessionDep, ma_hoc_phan: int, item_in: HocPhanUpdate) -> Any:
    item = hocphan_crud.get_hocphan(session=session, ma_hoc_phan=ma_hoc_phan)
    if not item:
        raise HTTPException(status_code=404, detail="HocPhan not found")
    item = hocphan_crud.update_hocphan(session=session, db_item=item, item_update=item_in)
    return item

@router.delete("/{ma_hoc_phan}", dependencies=[Depends(get_current_active_superuser)])
def delete_hocphan(session: SessionDep, ma_hoc_phan: int) -> Any:
    item = hocphan_crud.get_hocphan(session=session, ma_hoc_phan=ma_hoc_phan)
    if not item:
        raise HTTPException(status_code=404, detail="HocPhan not found")
    hocphan_crud.delete_hocphan(session=session, db_item=item)
    return {"message": "HocPhan deleted successfully"}
