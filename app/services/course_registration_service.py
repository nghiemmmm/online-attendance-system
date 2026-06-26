"""Provide course registration application services."""

from sqlmodel import Session

from app.crud import dangkyhocphan_crud
from app.models import (
    DangKyHocPhan,
    DangKyHocPhanCreate,
    DangKyHocPhanUpdate,
    Message,
)
from app.core.exceptions import CourseRegistrationNotFoundError


def list_course_registrations(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[DangKyHocPhan], int]:
    """Return paginated course registrations."""
    return dangkyhocphan_crud.get_course_registrations(
        session=session,
        skip=skip,
        limit=limit,
    )


def get_course_registration_or_404(
    *,
    session: Session,
    ma_dang_ky: int,
) -> DangKyHocPhan:
    """Return a course registration or raise a 404 error."""
    item = dangkyhocphan_crud.get_course_registration(
        session=session,
        ma_dang_ky=ma_dang_ky,
    )
    if not item:
        raise CourseRegistrationNotFoundError()
    return item


def create_course_registration(
    *,
    session: Session,
    item_in: DangKyHocPhanCreate,
) -> DangKyHocPhan:
    """Create a course registration."""
    return dangkyhocphan_crud.create_course_registration(
        session=session,
        item_create=item_in,
    )


def update_course_registration(
    *,
    session: Session,
    ma_dang_ky: int,
    item_in: DangKyHocPhanUpdate,
) -> DangKyHocPhan:
    """Update a course registration."""
    item = get_course_registration_or_404(
        session=session,
        ma_dang_ky=ma_dang_ky,
    )
    return dangkyhocphan_crud.update_course_registration(
        session=session,
        db_item=item,
        item_update=item_in,
    )


def delete_course_registration(*, session: Session, ma_dang_ky: int) -> Message:
    """Delete a course registration."""
    item = get_course_registration_or_404(
        session=session,
        ma_dang_ky=ma_dang_ky,
    )
    dangkyhocphan_crud.delete_course_registration(session=session, db_item=item)
    return Message(message="Course registration deleted successfully")
