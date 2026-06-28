"""
Class section service.

Contains logic for managing class section students, statistics, and warnings.
"""

from sqlmodel import Session, select, func
from fastapi import Depends, HTTPException
from typing import Any

from app.models import (
    Account,
    ClassSection,
    Student,
    CourseRegistration,
    ClassSession,
    Attendance,
)
from app.crud import class_section_crud, staff_crud
from app.api.deps import get_db


class ClassSectionService:
    """Service class for ClassSection-related database and business operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _ensure_authorized(self, class_section: ClassSection, current_account: Account) -> None:
        """Validate if the current lecturer/admin is authorized to access class section info."""
        if current_account.role == "ADMIN":
            return

        staff = staff_crud.get_staff_member_by_account_id(
            session=self.session, account_id=current_account.account_id
        )
        if not staff or class_section.staff_id != staff.staff_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view details of this class"
            )

    def get_class_section_students(
        self,
        class_section_id: int,
        current_account: Account,
    ) -> dict[str, Any]:
        """Lấy danh sách sinh viên trong lớp học phần."""
        item = class_section_crud.get_class_section(
            session=self.session, class_section_id=class_section_id
        )
        if not item:
            raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")

        self._ensure_authorized(item, current_account)

        statement = (
            select(Student)
            .join(CourseRegistration, CourseRegistration.student_id == Student.student_id)
            .where(CourseRegistration.class_section_id == class_section_id)
        )
        students = self.session.exec(statement).all()
        return {"data": students, "count": len(students)}

    def get_class_section_statistics(
        self,
        class_section_id: int,
        current_account: Account,
    ) -> dict[str, Any]:
        """Lấy thống kê điểm danh của lớp học phần."""
        item = class_section_crud.get_class_section(
            session=self.session, class_section_id=class_section_id
        )
        if not item:
            raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")

        self._ensure_authorized(item, current_account)

        student_count = self.session.exec(
            select(func.count())
            .select_from(CourseRegistration)
            .where(CourseRegistration.class_section_id == class_section_id)
        ).one()

        class_session_count = self.session.exec(
            select(func.count())
            .select_from(ClassSession)
            .where(
                ClassSession.class_section_id == class_section_id,
                ClassSession.status == "DA_KET_THUC",
            )
        ).one()

        statement = (
            select(Attendance.status, func.count(Attendance.attendance_id))
            .join(ClassSession, ClassSession.class_session_id == Attendance.class_session_id)
            .where(ClassSession.class_section_id == class_section_id)
            .group_by(Attendance.status)
        )
        stats = self.session.exec(statement).all()

        return {
            "student_count": student_count,
            "class_session_count": class_session_count,
            "detail": {stat[0]: stat[1] for stat in stats}
        }

    def get_class_section_warnings(
        self,
        class_section_id: int,
        current_account: Account,
        absence_limit: float = 20.0,
    ) -> dict[str, Any]:
        """Lấy danh sách cảnh báo chuyên cần sinh viên lớp học phần."""
        item = class_section_crud.get_class_section(
            session=self.session, class_section_id=class_section_id
        )
        if not item:
            raise HTTPException(status_code=404, detail="Lớp học phần không tồn tại")

        self._ensure_authorized(item, current_account)

        total_sessions = self.session.exec(
            select(func.count(ClassSession.class_session_id)).where(
                ClassSession.class_section_id == class_section_id,
                ClassSession.status == "DA_KET_THUC",
            )
        ).first() or 0

        statement = (
            select(Student)
            .join(CourseRegistration, CourseRegistration.student_id == Student.student_id)
            .where(CourseRegistration.class_section_id == class_section_id)
            .order_by(Student.student_id)
        )
        students = self.session.exec(statement).all()

        data = []
        for student in students:
            absent_count = self.session.exec(
                select(func.count(Attendance.attendance_id))
                .join(ClassSession, ClassSession.class_session_id == Attendance.class_session_id)
                .where(
                    ClassSession.class_section_id == class_section_id,
                    Attendance.student_id == student.student_id,
                    Attendance.status.in_(["VANG", "VANG_MAT"]),
                )
            ).first() or 0
            absence_rate = (
                round(absent_count / total_sessions * 100, 2)
                if total_sessions
                else 0.0
            )
            if absence_rate >= absence_limit:
                warning_status = "VUOT_NGUONG"
            elif absence_rate >= max(absence_limit - 5, 0):
                warning_status = "CANH_BAO"
            else:
                warning_status = "AN_TOAN"

            if warning_status != "AN_TOAN":
                data.append(
                    {
                        "student_id": student.student_id,
                        "full_name": f"{student.last_name} {student.first_name}".strip(),
                        "absent_session_count": absent_count,
                        "total_sessions": total_sessions,
                        "absence_rate": absence_rate,
                        "warning_status": warning_status,
                    }
                )

        return {"data": data, "count": len(data)}


def get_class_section_service(
    session: Session = Depends(get_db),
) -> ClassSectionService:
    """Dependency provider for ClassSectionService."""
    return ClassSectionService(session)
