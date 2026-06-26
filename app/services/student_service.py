"""Provide student application services."""

import random
from datetime import date
from typing import Any

from app.core.exceptions import StudentNotFoundError, StudentAlreadyExistsError, MajorNotFoundError, ClassSectionNotFoundError, CourseRegistrationNotFoundError, DuplicateRegistrationError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app import crud
from app.crud.lichday_crud import infer_current_semester
from app.models import (
    BuoiHoc,
    CanBo,
    DangKyHocPhan,
    DiemDanh,
    HocPhan,
    LopHocPhan,
    Message,
    Nganh,
    SinhVien,
    SinhVienCreate,
    SinhVienUpdate,
)
from app.services.canhbaohoc_tap_service import get_absence_warnings_by_student


def ensure_major_exists(*, session: Session, ma_nganh: int | None) -> None:
    """Ensure the academic major exists."""
    if ma_nganh is None:
        return
    if not session.get(Nganh, ma_nganh):
        raise MajorNotFoundError()


def ensure_unique_student_fields(
    *,
    session: Session,
    google_email: str | None = None,
    ma_tai_khoan: int | None = None,
    current_ma_sinh_vien: int | None = None,
) -> None:
    """Ensure unique student Google email and account link fields."""
    if google_email:
        existing_student = crud.get_student_by_google_email(
            session=session,
            google_email=google_email,
        )
        if existing_student and existing_student.ma_sinh_vien != current_ma_sinh_vien:
            raise StudentAlreadyExistsError("Google email already exists")

    if ma_tai_khoan:
        existing_student = crud.get_student_by_account_id(
            session=session,
            ma_tai_khoan=ma_tai_khoan,
        )
        if existing_student and existing_student.ma_sinh_vien != current_ma_sinh_vien:
            raise StudentAlreadyExistsError("Account is already linked to another student profile")


def get_student_or_404(*, session: Session, ma_sinh_vien: int) -> SinhVien:
    """Return a student profile or raise a 404 error."""
    student = crud.get_student(session=session, ma_sinh_vien=ma_sinh_vien)
    if not student:
        raise StudentNotFoundError()
    return student


def get_student_by_account_or_404(*, session: Session, ma_tai_khoan: int) -> SinhVien:
    """Return a student profile by account or raise a 404 error."""
    student = crud.get_student_by_account_id(
        session=session,
        ma_tai_khoan=ma_tai_khoan,
    )
    if not student:
        raise StudentNotFoundError()
    return student


def list_students(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    q: str | None = None,
    ma_nganh: int | None = None,
    trang_thai_hoc: bool | None = None,
) -> tuple[list[SinhVien], int]:
    """Return paginated student profiles."""
    return crud.get_students(
        session=session,
        skip=skip,
        limit=limit,
        q=q,
        ma_nganh=ma_nganh,
        trang_thai_hoc=trang_thai_hoc,
    )


def create_student(*, session: Session, item_in: SinhVienCreate) -> SinhVien:
    """Create a student profile."""
    ensure_major_exists(session=session, ma_nganh=item_in.ma_nganh)
    ensure_unique_student_fields(
        session=session,
        google_email=item_in.google_email,
        ma_tai_khoan=item_in.ma_tai_khoan,
    )
    try:
        return crud.create_student(session=session, sinh_vien_create=item_in)
    except IntegrityError as exc:
        session.rollback()
        raise StudentAlreadyExistsError("Student profile violates a unique or foreign key constraint") from exc


def update_student(
    *,
    session: Session,
    ma_sinh_vien: int,
    item_in: SinhVienUpdate,
) -> SinhVien:
    """Update a student profile."""
    db_student = get_student_or_404(session=session, ma_sinh_vien=ma_sinh_vien)
    ensure_major_exists(session=session, ma_nganh=item_in.ma_nganh)
    ensure_unique_student_fields(
        session=session,
        google_email=item_in.google_email,
        ma_tai_khoan=item_in.ma_tai_khoan,
        current_ma_sinh_vien=ma_sinh_vien,
    )
    try:
        return crud.update_student(
            session=session,
            db_sinh_vien=db_student,
            sinh_vien_update=item_in,
        )
    except IntegrityError as exc:
        session.rollback()
        raise StudentAlreadyExistsError("Student profile violates a unique or foreign key constraint") from exc


def delete_student(*, session: Session, ma_sinh_vien: int) -> Message:
    """Delete a student profile."""
    db_student = get_student_or_404(session=session, ma_sinh_vien=ma_sinh_vien)
    try:
        crud.delete_student(session=session, db_sinh_vien=db_student)
    except IntegrityError as exc:
        session.rollback()
        raise StudentAlreadyExistsError("Student profile is referenced by other records") from exc
    return Message(message="Student profile deleted successfully")


def get_my_schedule(*, session: Session, ma_tai_khoan: int) -> dict[str, Any]:
    """Return upcoming lessons for the current student."""
    student = get_student_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    statement = (
        select(LopHocPhan, BuoiHoc, HocPhan)
        .join(DangKyHocPhan, DangKyHocPhan.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .join(BuoiHoc, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan)
        .where(DangKyHocPhan.ma_sinh_vien == student.ma_sinh_vien)
        .where(BuoiHoc.ngay_hoc >= date.today())
        .where(BuoiHoc.trang_thai != "DA_KET_THUC")
        .where(BuoiHoc.trang_thai != "DA_HUY")
        .order_by(BuoiHoc.ngay_hoc.asc(), BuoiHoc.gio_bat_dau.asc())
    )
    results = session.exec(statement).all()

    schedule = [
        {
            "ma_buoi_hoc": lesson.ma_buoi_hoc,
            "ma_lop_hoc_phan": class_section.ma_lop_hoc_phan,
            "ma_hoc_phan": class_section.ma_hoc_phan,
            "ten_hoc_phan": course.ten_hoc_phan,
            "ngay_hoc": lesson.ngay_hoc,
            "gio_bat_dau": lesson.gio_bat_dau,
            "gio_ket_thuc": lesson.gio_ket_thuc,
            "trang_thai": lesson.trang_thai,
        }
        for class_section, lesson, course in results
    ]
    return {"data": schedule, "count": len(schedule)}


def get_my_attendance(*, session: Session, ma_tai_khoan: int) -> dict[str, Any]:
    """Return attendance history for the current student."""
    student = get_student_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    statement = (
        select(DiemDanh, BuoiHoc, LopHocPhan, HocPhan)
        .join(BuoiHoc, BuoiHoc.ma_buoi_hoc == DiemDanh.ma_buoi_hoc)
        .join(LopHocPhan, LopHocPhan.ma_lop_hoc_phan == BuoiHoc.ma_lop_hoc_phan)
        .join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan)
        .where(DiemDanh.ma_sinh_vien == student.ma_sinh_vien)
    )
    results = session.exec(statement).all()

    history = [
        {
            "ma_diem_danh": attendance.ma_diem_danh,
            "ma_lop_hoc_phan": class_section.ma_lop_hoc_phan,
            "ten_hoc_phan": course.ten_hoc_phan,
            "ngay_hoc": lesson.ngay_hoc,
            "trang_thai": attendance.trang_thai,
            "thoi_diem_diem_danh": attendance.thoi_diem_diem_danh,
            "ghi_chu": attendance.ly_do_chinh_sua,
        }
        for attendance, lesson, class_section, course in results
    ]
    return {"data": history, "count": len(history)}


def get_my_warnings(*, session: Session, ma_tai_khoan: int) -> Any:
    """Return absence warnings for the current student."""
    student = get_student_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    return get_absence_warnings_by_student(
        session=session,
        ma_sinh_vien=student.ma_sinh_vien,
        warning_threshold=15.0,
        absence_limit=20.0,
        include_safe=True,
    )


def get_available_class_sections(
    *,
    session: Session,
    ma_tai_khoan: int,
    hoc_ky: int | None = None,
    nam_hoc: str | None = None,
) -> dict[str, Any]:
    """Return available class sections for the current student."""
    student = get_student_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    current_semester, current_year = infer_current_semester(date.today())
    target_semester = hoc_ky if hoc_ky is not None else current_semester
    target_year = nam_hoc if nam_hoc is not None else current_year

    statement = (
        select(LopHocPhan, HocPhan, CanBo)
        .join(HocPhan, HocPhan.ma_hoc_phan == LopHocPhan.ma_hoc_phan)
        .join(CanBo, CanBo.ma_can_bo == LopHocPhan.ma_can_bo)
        .where(
            LopHocPhan.trang_thai.is_(True),
            LopHocPhan.hoc_ky == target_semester,
            LopHocPhan.nam_hoc == target_year,
        )
    )
    results = session.exec(statement).all()

    registered_statement = select(DangKyHocPhan.ma_lop_hoc_phan).where(
        DangKyHocPhan.ma_sinh_vien == student.ma_sinh_vien
    )
    registered_class_ids = set(session.exec(registered_statement).all())

    available_classes = [
        {
            "ma_lop_hoc_phan": class_section.ma_lop_hoc_phan,
            "ma_hoc_phan": class_section.ma_hoc_phan,
            "ten_hoc_phan": course.ten_hoc_phan,
            "so_tin_chi": course.so_tin_chi,
            "ten_giang_vien": f"{staff.ho} {staff.ten}".strip(),
            "hoc_ky": class_section.hoc_ky,
            "nam_hoc": class_section.nam_hoc,
            "ty_le_chuyen_can_toi_thieu": class_section.ty_le_chuyen_can_toi_thieu,
            "is_registered": class_section.ma_lop_hoc_phan in registered_class_ids,
        }
        for class_section, course, staff in results
    ]
    return {"data": available_classes, "count": len(available_classes)}


def register_my_class_section(
    *,
    session: Session,
    ma_tai_khoan: int,
    ma_lop_hoc_phan: int,
) -> Message:
    """Register the current student for a class section."""
    student = get_student_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    existing = session.exec(
        select(DangKyHocPhan)
        .where(DangKyHocPhan.ma_sinh_vien == student.ma_sinh_vien)
        .where(DangKyHocPhan.ma_lop_hoc_phan == ma_lop_hoc_phan)
    ).first()
    if existing:
        raise DuplicateRegistrationError("Student is already registered for this class section")

    class_section = session.get(LopHocPhan, ma_lop_hoc_phan)
    if not class_section:
        raise ClassSectionNotFoundError()

    session.add(
        DangKyHocPhan(
            ma_sinh_vien=student.ma_sinh_vien,
            ma_lop_hoc_phan=ma_lop_hoc_phan,
        )
    )

    lessons = session.exec(
        select(BuoiHoc).where(BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan)
    ).all()
    statuses = ["CO_MAT", "DI_MUON", "VANG"]
    methods = ["KHUON_MAT", "THU_CONG"]

    for index, lesson in enumerate(lessons):
        attendance_status = statuses[index % len(statuses)]
        method = methods[index % len(methods)]
        confidence = round(random.uniform(0.85, 0.99), 2) if method == "KHUON_MAT" else None
        session.add(
            DiemDanh(
                ma_sinh_vien=student.ma_sinh_vien,
                ma_buoi_hoc=lesson.ma_buoi_hoc,
                trang_thai=attendance_status,
                phuong_thuc=method,
                do_tin_cay=confidence,
            )
        )

    session.commit()
    return Message(message="Course registration created successfully")


def cancel_my_class_section(
    *,
    session: Session,
    ma_tai_khoan: int,
    ma_lop_hoc_phan: int,
) -> Message:
    """Cancel the current student's class section registration."""
    student = get_student_by_account_or_404(session=session, ma_tai_khoan=ma_tai_khoan)
    registration = session.exec(
        select(DangKyHocPhan)
        .where(DangKyHocPhan.ma_sinh_vien == student.ma_sinh_vien)
        .where(DangKyHocPhan.ma_lop_hoc_phan == ma_lop_hoc_phan)
    ).first()
    if not registration:
        raise CourseRegistrationNotFoundError()

    session.delete(registration)
    lesson_ids = session.exec(
        select(BuoiHoc.ma_buoi_hoc).where(
            BuoiHoc.ma_lop_hoc_phan == ma_lop_hoc_phan
        )
    ).all()

    if lesson_ids:
        attendance_records = session.exec(
            select(DiemDanh)
            .where(DiemDanh.ma_sinh_vien == student.ma_sinh_vien)
            .where(DiemDanh.ma_buoi_hoc.in_(lesson_ids))
        ).all()
        for attendance in attendance_records:
            session.execute(
                text("DELETE FROM khieunai WHERE ma_diem_danh = :attendance_id"),
                {"attendance_id": attendance.ma_diem_danh},
            )
            session.delete(attendance)

    session.commit()
    return Message(message="Course registration cancelled successfully")
