from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import ThoiKhoaBieu, ThoiKhoaBieuCreate, ThoiKhoaBieuUpdate, ThoiKhoaBieuPublic, ThoiKhoaBieusPublic
from app.crud import thoikhoabieu_crud

router = APIRouter(prefix="/thoikhoabieu", tags=["thoikhoabieu"])

@router.get("/", response_model=ThoiKhoaBieusPublic)
def read_thoikhoabieus(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    items, count = thoikhoabieu_crud.get_thoikhoabieus(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}

@router.get("/{ma_thoi_khoa_bieu}", response_model=ThoiKhoaBieuPublic)
def read_thoikhoabieu(session: SessionDep, ma_thoi_khoa_bieu: int) -> Any:
    item = thoikhoabieu_crud.get_thoikhoabieu(session=session, ma_thoi_khoa_bieu=ma_thoi_khoa_bieu)
    if not item:
        raise HTTPException(status_code=404, detail="ThoiKhoaBieu not found")
    return item

@router.post("/", response_model=ThoiKhoaBieuPublic, dependencies=[Depends(get_current_active_superuser)])
def create_thoikhoabieu(session: SessionDep, item_in: ThoiKhoaBieuCreate) -> Any:
    item = thoikhoabieu_crud.create_thoikhoabieu(session=session, item_create=item_in)
    return item

@router.patch("/{ma_thoi_khoa_bieu}", response_model=ThoiKhoaBieuPublic, dependencies=[Depends(get_current_active_superuser)])
def update_thoikhoabieu(session: SessionDep, ma_thoi_khoa_bieu: int, item_in: ThoiKhoaBieuUpdate) -> Any:
    item = thoikhoabieu_crud.get_thoikhoabieu(session=session, ma_thoi_khoa_bieu=ma_thoi_khoa_bieu)
    if not item:
        raise HTTPException(status_code=404, detail="ThoiKhoaBieu not found")
    item = thoikhoabieu_crud.update_thoikhoabieu(session=session, db_item=item, item_update=item_in)
    return item

@router.delete("/{ma_thoi_khoa_bieu}", dependencies=[Depends(get_current_active_superuser)])
def delete_thoikhoabieu(session: SessionDep, ma_thoi_khoa_bieu: int) -> Any:
    item = thoikhoabieu_crud.get_thoikhoabieu(session=session, ma_thoi_khoa_bieu=ma_thoi_khoa_bieu)
    if not item:
        raise HTTPException(status_code=404, detail="ThoiKhoaBieu not found")
    thoikhoabieu_crud.delete_thoikhoabieu(session=session, db_item=item)
    return {"message": "ThoiKhoaBieu deleted successfully"}
