"""Provide staff application services."""

from datetime import date
from typing import Any

from app.core.exceptions import StaffNotFoundError, StaffAlreadyExistsError, PermissionDeniedError, AppException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from app import crud
from app.models import (
    BuoiHoc,
    CanBo,
    CanBoCreate,
    CanBoUpdate,
    DangKyHocPhan,
    DiemDanh,
    HocPhan,
    LopHocPhan,
    Message,
    MonthlyAttendanceSummary,
)
from app.services.attendance_summary_service import get_monthly_attendance_summary
from app.services.khieunai_service import get_khieu_nai_cho_xu_ly_metric


def ensure_unique_staff_fields(
    *,
    session: Session,
    google_email: str | None = None,
    ma_tai_khoan: int | None = None,
    current_ma_can_bo: int | None = None,
) -> None:
    """Ensure unique staff Google email and account link fields."""
    if google_email:
        existing_staff = crud.get_staff_member_by_google_email(
            session=session,
            google_email=google_email,
        )
        if existing_staff and existing_staff.ma_can_bo != current_ma_can_bo:
            raise StaffAlreadyExistsError("Google email already exists")

    if ma_tai_khoan:
        existing_staff = crud.get_staff_member_by_account_id(
            session=session,
            ma_tai_khoan=ma_tai_khoan,
        )
        if existing_staff and existing_staff.ma_can_bo != current_ma_can_bo:
            raise StaffAlreadyExistsError("Account is already linked to another staff profile")


def get_staff_member_or_404(*, session: Session, ma_can_bo: int) -> CanBo:
    """Return a staff profile or raise a 404 error."""
    staff = crud.get_staff_member(session=session, ma_can_bo=ma_can_bo)
    if not staff:
        raise StaffNotFoundError("Staff profile not found")
    return staff


def get_staff_by_account_or_404(*, session: Session, ma_tai_khoan: int) -> CanBo:
    """Return a staff profile by account or raise a 404 error."""
    staff = crud.get_staff_member_by_account_id(
        session=session,
        ma_tai_khoan=ma_tai_khoan,
    )
    if not staff:
        raise StaffNotFoundError("Staff profile not found")
    return staff


def ensure_staff_owns_profile(
    *,
    session: Session,
    ma_can_bo: int,
    ma_tai_khoan: int,
) -> CanBo:
    """Ensure the staff profile belongs to the current account."""
    staff = get_staff_member_or_404(session=session, ma_can_bo=ma_can_bo)
    if staff.ma_tai_khoan != ma_tai_khoan:
        raise PermissionDeniedError("Not authorized to access this staff profile")
    return staff


def list_staff_members(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    trang_thai: bool | None = None,
) -> tuple[list[CanBo], int]:
    """Return paginated staff profiles."""
    return crud.get_staff_members(
        session=session,
        skip=skip,
        limit=limit,
        q=q,
        trang_thai=trang_thai,
    )


def create_staff_member(*, session: Session, item_in: CanBoCreate) -> CanBo:
    """Create a staff profile."""
    ensure_unique_staff_fields(
        session=session,
        google_email=item_in.google_email,
        ma_tai_khoan=item_in.ma_tai_khoan,
    )
    try:
        return crud.create_staff_member(session=session, can_bo_create=item_in)
    except IntegrityError as exc:
        session.rollback()
        raise StaffAlreadyExistsError("Staff profile violates a unique or foreign key constraint") from exc


def update_staff_member(
    *,
    session: Session,
    ma_can_bo: int,
    item_in: CanBoUpdate,
) -> CanBo:
    """Update a staff profile."""
    db_staff = get_staff_member_or_404(session=session, ma_can_bo=ma_can_bo)
    ensure_unique_staff_fields(
        session=session,
        google_email=item_in.google_email,
        ma_tai_khoan=item_in.ma_tai_khoan,
        current_ma_can_bo=ma_can_bo,
    )
    try:
        return crud.update_staff_member(
            session=session,
            db_can_bo=db_staff,
            can_bo_update=item_in,
        )
    except IntegrityError as exc:
        session.rollback()
        raise StaffAlreadyExistsError("Staff profile violates a unique or foreign key constraint") from exc


def delete_staff_member(*, session: Session, ma_can_bo: int) -> Message:
    """Delete a staff profile."""
    db_staff = get_staff_member_or_404(session=session, ma_can_bo=ma_can_bo)
    try:
        crud.delete_staff_member(session=session, db_can_bo=db_staff)
    except IntegrityError as exc:
        session.rollback()
        raise StaffAlreadyExistsError("Staff profile is referenced by other records") from exc
    return Message(message="Staff profile deleted successfully")


def read_my_teaching_schedule(
    *,
    session: Session,
    ma_tai_khoan: int,
    from_date: date | None = None,
    to_date: date | None = None,
    hoc_ky: int | None = None,
    nam_hoc: str | None = None,
    trang_thai: bool | None = None,
    skip: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    """Return the current staff member's teaching schedule."""
    staff = get_staff_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    items, count = crud.get_teaching_schedule_by_staff_member(
        session=session,
        ma_can_bo=staff.ma_can_bo,
        from_date=from_date,
        to_date=to_date,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
        trang_thai=trang_thai,
        skip=skip,
        limit=limit,
    )
    return {"data": items, "count": count}


def read_my_class_sections(*, session: Session, ma_tai_khoan: int) -> dict[str, Any]:
    """Return class sections taught by the current staff member."""
    staff = get_staff_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    statement = (
        select(LopHocPhan, HocPhan)
        .join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan)
        .where(LopHocPhan.ma_can_bo == staff.ma_can_bo)
    )
    results = session.exec(statement).all()

    class_sections = []
    for class_section, course in results:
        registration_count = session.exec(
            select(func.count(DangKyHocPhan.ma_sinh_vien)).where(
                DangKyHocPhan.ma_lop_hoc_phan == class_section.ma_lop_hoc_phan
            )
        ).first() or 0
        class_sections.append(
            {
                "ma_lop_hoc_phan": class_section.ma_lop_hoc_phan,
                "ma_hoc_phan": class_section.ma_hoc_phan,
                "ten_hoc_phan": course.ten_hoc_phan,
                "hoc_ky": class_section.hoc_ky,
                "nam_hoc": class_section.nam_hoc,
                "trang_thai": class_section.trang_thai,
                "si_so_hien_tai": registration_count,
            }
        )
    return {"data": class_sections, "count": len(class_sections)}


def read_staff_teaching_schedule(
    *,
    session: Session,
    current_account_id: int,
    ma_can_bo: int,
    from_date: date | None = None,
    to_date: date | None = None,
    hoc_ky: int | None = None,
    nam_hoc: str | None = None,
    trang_thai: bool | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Any], int]:
    """Return teaching schedule for an authorized staff profile."""
    if from_date and to_date and from_date > to_date:
        raise AppException("from_date must be before or equal to to_date", status_code=400)
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account_id,
    )
    return crud.get_teaching_schedule_by_staff_member(
        session=session,
        ma_can_bo=ma_can_bo,
        from_date=from_date,
        to_date=to_date,
        hoc_ky=hoc_ky,
        nam_hoc=nam_hoc,
        trang_thai=trang_thai,
        skip=skip,
        limit=limit,
    )


def read_staff_recent_lessons(
    *,
    session: Session,
    current_account_id: int,
    ma_can_bo: int,
    limit: int = 5,
) -> tuple[list[Any], int]:
    """Return recent lessons for an authorized staff profile."""
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account_id,
    )
    return crud.get_recent_lessons_by_staff_member(
        session=session,
        ma_can_bo=ma_can_bo,
        limit=limit,
    )


def count_current_teaching_class_sections(
    *,
    session: Session,
    current_account_id: int,
    ma_can_bo: int,
    as_of_date: date | None = None,
) -> tuple[int, int, str, date]:
    """Return active teaching class section count for a staff profile."""
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account_id,
    )
    target_date = as_of_date or date.today()
    count, hoc_ky, nam_hoc = crud.count_current_teaching_class_sections_by_staff_member(
        session=session,
        ma_can_bo=ma_can_bo,
        as_of_date=target_date,
    )
    return count, hoc_ky, nam_hoc, target_date


def read_monthly_attendance_summary(
    *,
    session: Session,
    current_account_id: int,
    ma_can_bo: int,
    reference_date: date | None = None,
) -> MonthlyAttendanceSummary:
    """Return monthly attendance summary for an authorized staff profile."""
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account_id,
    )
    return get_monthly_attendance_summary(
        session=session,
        ma_can_bo=ma_can_bo,
        reference_date=reference_date or date.today(),
    )


def read_pending_appeal_count(
    *,
    session: Session,
    current_account_id: int,
    ma_can_bo: int,
) -> Any:
    """Return pending appeal count for an authorized staff profile."""
    ensure_staff_owns_profile(
        session=session,
        ma_can_bo=ma_can_bo,
        ma_tai_khoan=current_account_id,
    )
    return get_khieu_nai_cho_xu_ly_metric(session=session, ma_can_bo=ma_can_bo)


def read_my_reports(*, session: Session, ma_tai_khoan: int) -> list[dict[str, Any]]:
    """Return attendance reports for classes taught by the current staff member."""
    staff = get_staff_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    results = session.exec(
        select(LopHocPhan, HocPhan)
        .join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan)
        .where(LopHocPhan.ma_can_bo == staff.ma_can_bo)
    ).all()

    reports = []
    for class_section, course in results:
        student_count = session.exec(
            select(func.count(DangKyHocPhan.ma_sinh_vien)).where(
                DangKyHocPhan.ma_lop_hoc_phan == class_section.ma_lop_hoc_phan
            )
        ).first() or 0
        total_sessions = session.exec(
            select(func.count(BuoiHoc.ma_buoi_hoc)).where(
                BuoiHoc.ma_lop_hoc_phan == class_section.ma_lop_hoc_phan
            )
        ).first() or 0
        completed_sessions = session.exec(
            select(BuoiHoc)
            .where(
                BuoiHoc.ma_lop_hoc_phan == class_section.ma_lop_hoc_phan,
                BuoiHoc.trang_thai == "DA_KET_THUC",
            )
            .order_by(BuoiHoc.so_buoi)
        ).all()
        attendances = session.exec(
            select(DiemDanh)
            .join(BuoiHoc)
            .where(BuoiHoc.ma_lop_hoc_phan == class_section.ma_lop_hoc_phan)
        ).all()

        present_count = len(
            [attendance for attendance in attendances if attendance.trang_thai == "CO_MAT"]
        )
        late_count = len(
            [
                attendance
                for attendance in attendances
                if attendance.trang_thai in ["DI_MUON", "MUON"]
            ]
        )
        total_attendance_count = len(attendances)
        average_rate = (
            round(((present_count + late_count) / total_attendance_count * 100), 1)
            if total_attendance_count > 0
            else 0.0
        )

        data_points = []
        for lesson in completed_sessions:
            lesson_attendances = [
                attendance
                for attendance in attendances
                if attendance.ma_buoi_hoc == lesson.ma_buoi_hoc
            ]
            data_points.append(
                {
                    "date": lesson.ngay_hoc.strftime("%d/%m")
                    + f" (Buoi {lesson.so_buoi or 1})",
                    "present": len(
                        [
                            attendance
                            for attendance in lesson_attendances
                            if attendance.trang_thai == "CO_MAT"
                        ]
                    ),
                    "late": len(
                        [
                            attendance
                            for attendance in lesson_attendances
                            if attendance.trang_thai in ["DI_MUON", "MUON"]
                        ]
                    ),
                    "absent": len(
                        [
                            attendance
                            for attendance in lesson_attendances
                            if attendance.trang_thai == "VANG"
                        ]
                    ),
                }
            )

        reports.append(
            {
                "id": str(class_section.ma_lop_hoc_phan),
                "subjectCode": f"HP{class_section.ma_hoc_phan}",
                "subjectName": course.ten_hoc_phan,
                "totalStudents": student_count,
                "completedSessions": len(completed_sessions),
                "totalSessions": total_sessions,
                "averageAttendanceRate": average_rate,
                "dataPoints": data_points,
            }
        )
    return reports
