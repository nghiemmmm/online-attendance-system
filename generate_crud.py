import os

MODELS = [
    ("Nganh", "nganh", "ma_nganh"),
    ("HocPhan", "hocphan", "ma_hoc_phan"),
    ("LopHocPhan", "lophocphan", "ma_lop_hoc_phan"),
    ("BuoiHoc", "buoihoc", "ma_buoi_hoc"),
    ("DangKyHocPhan", "dangkyhocphan", "ma_dang_ky"),
    ("ThoiKhoaBieu", "thoikhoabieu", "ma_thoi_khoa_bieu"),
]

def generate_crud(model_name, module_name, pk):
    return f"""from sqlmodel import Session, select, func
from app.models import {model_name}, {model_name}Create, {model_name}Update

def get_{module_name}(*, session: Session, {pk}: int) -> {model_name} | None:
    return session.get({model_name}, {pk})

def get_{module_name}s(*, session: Session, skip: int = 0, limit: int = 100) -> tuple[list[{model_name}], int]:
    count_statement = select(func.count()).select_from({model_name})
    count = session.exec(count_statement).one()
    statement = select({model_name}).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return list(items), count

def create_{module_name}(*, session: Session, item_create: {model_name}Create) -> {model_name}:
    db_item = {model_name}.model_validate(item_create)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def update_{module_name}(*, session: Session, db_item: {model_name}, item_update: {model_name}Update) -> {model_name}:
    item_data = item_update.model_dump(exclude_unset=True)
    for field, value in item_data.items():
        setattr(db_item, field, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def delete_{module_name}(*, session: Session, db_item: {model_name}) -> None:
    session.delete(db_item)
    session.commit()
"""

def generate_router(model_name, module_name, pk):
    return f"""from typing import Any
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import {model_name}, {model_name}Create, {model_name}Update, {model_name}Public, {model_name}sPublic
from app.crud import {module_name}_crud

router = APIRouter(prefix="/{module_name.replace('_', '-')}", tags=["{module_name.replace('_', '-')}"])

@router.get("/", response_model={model_name}sPublic)
def read_{module_name}s(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    items, count = {module_name}_crud.get_{module_name}s(session=session, skip=skip, limit=limit)
    return {{"data": items, "count": count}}

@router.get("/{{{pk}}}", response_model={model_name}Public)
def read_{module_name}(session: SessionDep, {pk}: int) -> Any:
    item = {module_name}_crud.get_{module_name}(session=session, {pk}={pk})
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return item

@router.post("/", response_model={model_name}Public, dependencies=[Depends(get_current_active_superuser)])
def create_{module_name}(session: SessionDep, item_in: {model_name}Create) -> Any:
    item = {module_name}_crud.create_{module_name}(session=session, item_create=item_in)
    return item

@router.patch("/{{{pk}}}", response_model={model_name}Public, dependencies=[Depends(get_current_active_superuser)])
def update_{module_name}(session: SessionDep, {pk}: int, item_in: {model_name}Update) -> Any:
    item = {module_name}_crud.get_{module_name}(session=session, {pk}={pk})
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    item = {module_name}_crud.update_{module_name}(session=session, db_item=item, item_update=item_in)
    return item

@router.delete("/{{{pk}}}", dependencies=[Depends(get_current_active_superuser)])
def delete_{module_name}(session: SessionDep, {pk}: int) -> Any:
    item = {module_name}_crud.get_{module_name}(session=session, {pk}={pk})
    if not item:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    {module_name}_crud.delete_{module_name}(session=session, db_item=item)
    return {{"message": "{model_name} deleted successfully"}}
"""

def generate_all():
    crud_dir = "app/crud"
    route_dir = "app/api/routes"
    
    for model_name, module_name, pk in MODELS:
        # Generate CRUD
        crud_path = os.path.join(crud_dir, f"{module_name}_crud.py")
        if not os.path.exists(crud_path):
            with open(crud_path, "w", encoding="utf-8") as f:
                f.write(generate_crud(model_name, module_name, pk))
            print(f"Created {crud_path}")
        
        # Generate Router
        route_path = os.path.join(route_dir, f"{module_name}.py")
        if not os.path.exists(route_path):
            with open(route_path, "w", encoding="utf-8") as f:
                f.write(generate_router(model_name, module_name, pk))
            print(f"Created {route_path}")

if __name__ == "__main__":
    generate_all()
