from typing import Any
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import Nganh, NganhCreate, NganhUpdate, NganhPublic, NganhsPublic
from app.crud import nganh_crud

router = APIRouter(prefix="/nganh", tags=["nganh"])

@router.get("/", response_model=NganhsPublic)
def read_nganhs(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    items, count = nganh_crud.get_nganhs(session=session, skip=skip, limit=limit)
    return {"data": items, "count": count}

@router.get("/{ma_nganh}", response_model=NganhPublic)
def read_nganh(session: SessionDep, ma_nganh: int) -> Any:
    item = nganh_crud.get_nganh(session=session, ma_nganh=ma_nganh)
    if not item:
        raise HTTPException(status_code=404, detail="Nganh not found")
    return item

@router.post("/", response_model=NganhPublic, dependencies=[Depends(get_current_active_superuser)])
def create_nganh(session: SessionDep, item_in: NganhCreate) -> Any:
    item = nganh_crud.create_nganh(session=session, item_create=item_in)
    return item

@router.patch("/{ma_nganh}", response_model=NganhPublic, dependencies=[Depends(get_current_active_superuser)])
def update_nganh(session: SessionDep, ma_nganh: int, item_in: NganhUpdate) -> Any:
    item = nganh_crud.get_nganh(session=session, ma_nganh=ma_nganh)
    if not item:
        raise HTTPException(status_code=404, detail="Nganh not found")
    item = nganh_crud.update_nganh(session=session, db_item=item, item_update=item_in)
    return item

@router.delete("/{ma_nganh}", dependencies=[Depends(get_current_active_superuser)])
def delete_nganh(session: SessionDep, ma_nganh: int) -> Any:
    item = nganh_crud.get_nganh(session=session, ma_nganh=ma_nganh)
    if not item:
        raise HTTPException(status_code=404, detail="Nganh not found")
    nganh_crud.delete_nganh(session=session, db_item=item)
    return {"message": "Nganh deleted successfully"}
