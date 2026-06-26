"""
Lich hoc service.

Contains business logic for student study schedules.
"""

from datetime import date
from sqlmodel import Session

from app.crud.lichhoc_crud import get_today_schedule_by_student
from app.crud.sinhvien_crud import get_student
from app.models import LichHocHomNayPublic
from app.core.exceptions import StudentNotFoundError


def get_today_schedule(
    *,
    session: Session,
    ma_sinh_vien: int,
    target_date: date,
) -> LichHocHomNayPublic:
    """Lay lich hoc trong ngay cua sinh vien."""
    if not get_student(session=session, ma_sinh_vien=ma_sinh_vien):
        raise StudentNotFoundError("Student profile not found")

    items, count = get_today_schedule_by_student(
        session=session,
        ma_sinh_vien=ma_sinh_vien,
        target_date=target_date,
    )
    return LichHocHomNayPublic(
        ma_sinh_vien=ma_sinh_vien,
        ngay_hoc=target_date,
        data=items,
        count=count,
    )
