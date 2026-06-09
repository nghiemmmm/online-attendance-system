"""
Sinh vien router.

Defines APIs for managing student profiles.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import IntegrityError

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Message,
    Nganh,
    SinhVienCreate,
    SinhVienPublic,
    SinhViensPublic,
    SinhVienUpdate,
)

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
