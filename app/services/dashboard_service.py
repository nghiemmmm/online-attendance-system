"""
Dashboard service.

Contains logic for admin dashboard statistics and system reports.
"""

from sqlmodel import Session, select, func, col
from fastapi import Depends
from typing import Any
from datetime import datetime

from app.models import (
    Account,
    Student,
    Staff,
    ClassSection,
    Attendance,
    FaceImage,
    Major,
    Course,
    ClassSession,
    CourseRegistration,
)
from app.api.deps import get_db


class DashboardService:
    """Service to handle dashboard analytics and system reporting."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_system_stats(self) -> dict[str, Any]:
        """Lấy số liệu thống kê hệ thống dành cho Admin."""
        total_users = self.session.exec(select(func.count(Account.account_id))).first() or 0
        total_students = self.session.exec(
            select(func.count(Account.account_id)).where(Account.role == "SINH_VIEN")
        ).first() or 0
        total_lecturers = self.session.exec(
            select(func.count(Account.account_id)).where(Account.role.in_(["GIANG_VIEN", "CAN_BO"]))
        ).first() or 0
        total_admins = self.session.exec(
            select(func.count(Account.account_id)).where(Account.role == "ADMIN")
        ).first() or 0

        total_classes = self.session.exec(select(func.count(ClassSection.class_section_id))).first() or 0

        # Calculate true average attendance rate: total present/late vs expected enrollments of active/completed sessions
        class_sessions = self.session.exec(
            select(ClassSession).where(ClassSession.status.in_(["DANG_DIEN_RA", "DA_KET_THUC"]))
        ).all()

        total_expected = 0
        for class_session in class_sessions:
            reg_count = self.session.exec(
                select(func.count(CourseRegistration.student_id))
                .where(CourseRegistration.class_section_id == class_session.class_section_id)
            ).first() or 0
            total_expected += reg_count

        class_session_ids = [
            class_session.class_session_id for class_session in class_sessions
        ]
        if class_session_ids and total_expected > 0:
            total_present = self.session.exec(
                select(func.count(Attendance.attendance_id))
                .where(
                    Attendance.status.in_(["CO_MAT", "DI_MUON", "MUON"]),
                    Attendance.class_session_id.in_(class_session_ids)
                )
            ).first() or 0
            avg_rate = total_present / total_expected
        else:
            avg_rate = 0.0

        subquery = select(FaceImage.student_id).distinct()
        stmt = select(func.count(Student.student_id)).where(Student.student_id.not_in(subquery))
        students_without_face = self.session.exec(stmt).first() or 0

        return {
            "total_users": total_users,
            "total_students": total_students,
            "total_lecturers": total_lecturers,
            "total_admins": total_admins,
            "total_classes": total_classes,
            "avg_attendance_rate": avg_rate,
            "students_without_face": students_without_face
        }

    def get_system_reports(self) -> dict[str, Any]:
        """Lấy dữ liệu thống kê báo cáo chi tiết cho Admin."""
        # 1. Summary Metrics
        total_students = self.session.exec(select(func.count(Student.student_id))).first() or 0
        # Calculate true average attendance rate: total present/late vs expected enrollments of active/completed sessions
        class_sessions = self.session.exec(
            select(ClassSession).where(ClassSession.status.in_(["DANG_DIEN_RA", "DA_KET_THUC"]))
        ).all()

        total_expected = 0
        for class_session in class_sessions:
            reg_count = self.session.exec(
                select(func.count(CourseRegistration.student_id))
                .where(CourseRegistration.class_section_id == class_session.class_section_id)
            ).first() or 0
            total_expected += reg_count

        class_session_ids = [
            class_session.class_session_id for class_session in class_sessions
        ]
        if class_session_ids and total_expected > 0:
            total_present = self.session.exec(
                select(func.count(Attendance.attendance_id))
                .where(
                    Attendance.status.in_(["CO_MAT", "DI_MUON", "MUON"]),
                    Attendance.class_session_id.in_(class_session_ids)
                )
            ).first() or 0
            avg_rate = round((total_present / total_expected * 100), 1)
        else:
            avg_rate = 0.0

        total_sessions = self.session.exec(
            select(func.count(ClassSession.class_session_id)).where(ClassSession.status == "DA_KET_THUC")
        ).first() or 0

        # Cảnh báo: Số sinh viên có trên 3 buổi Vắng
        statement_warning = (
            select(Attendance.student_id)
            .where(Attendance.status == "VANG")
            .group_by(Attendance.student_id)
            .having(func.count(Attendance.attendance_id) >= 3)
        )
        attendance_warnings = len(self.session.exec(statement_warning).all())

        # 2. attendance_by_department
        dept_data = {}
        all_majors = self.session.exec(select(Major)).all()
        for major in all_majors:
            dept_data[major.major_id] = {
                "department": major.major_name,
                "present": 0,
                "absent": 0,
                "late": 0,
                "rate": 0.0
            }

        statement_dept = (
            select(Student.major_id, Attendance.status, func.count(Attendance.attendance_id))
            .join(Attendance, Attendance.student_id == Student.student_id)
            .group_by(Student.major_id, Attendance.status)
        )
        dept_results = self.session.exec(statement_dept).all()
        for major_id, status, count in dept_results:
            if major_id in dept_data:
                if status == "CO_MAT":
                    dept_data[major_id]["present"] += count
                elif status == "VANG":
                    dept_data[major_id]["absent"] += count
                elif status in ["DI_MUON", "MUON"]:
                    dept_data[major_id]["late"] += count

        for major_id, info in list(dept_data.items()):
            total = info["present"] + info["absent"] + info["late"]
            info["rate"] = (
                round(((info["present"] + info["late"]) / total * 100), 1)
                if total > 0
                else 0.0
            )

        attendance_by_department = list(dept_data.values())
        if not attendance_by_department:
            attendance_by_department = [
                {"department": "CNTT", "present": 0, "absent": 0, "late": 0, "rate": 0.0},
                {"department": "QTKD", "present": 0, "absent": 0, "late": 0, "rate": 0.0}
            ]

        # 3. status_distribution
        present_count = (
            self.session.exec(
                select(func.count(Attendance.attendance_id)).where(
                    Attendance.status == "CO_MAT"
                )
            ).first()
            or 0
        )
        absent_count = (
            self.session.exec(
                select(func.count(Attendance.attendance_id)).where(
                    Attendance.status == "VANG"
                )
            ).first()
            or 0
        )
        late_count = (
            self.session.exec(
                select(func.count(Attendance.attendance_id)).where(
                    Attendance.status.in_(["DI_MUON", "MUON"])
                )
            ).first()
            or 0
        )
        leave_count = (
            self.session.exec(
                select(func.count(Attendance.attendance_id)).where(
                    Attendance.status == "XIN_PHEP"
                )
            ).first()
            or 0
        )

        status_distribution = [
            {"name": "Co mat", "value": present_count, "color": "#22c55e"},
            {"name": "Vang mat", "value": absent_count, "color": "#ef4444"},
            {"name": "Di tre", "value": late_count, "color": "#f59e0b"},
            {"name": "Xin phep", "value": leave_count, "color": "#3b82f6"},
        ]

        # 4. weekly_trend (last 7 days of completed sessions)
        statement_weekly = (
            select(ClassSession.class_date, Attendance.status, func.count(Attendance.attendance_id))
            .join(Attendance, Attendance.class_session_id == ClassSession.class_session_id)
            .group_by(ClassSession.class_date, Attendance.status)
            .order_by(ClassSession.class_date.desc())
            .limit(21)
        )
        weekly_results = self.session.exec(statement_weekly).all()
        weekly_dict = {}
        for ngay, status, count in weekly_results:
            date_label = ngay.strftime("%d/%m")
            if date_label not in weekly_dict:
                weekly_dict[date_label] = {"present": 0, "late": 0, "absent": 0}
            if status == "CO_MAT":
                weekly_dict[date_label]["present"] += count
            elif status in ["DI_MUON", "MUON"]:
                weekly_dict[date_label]["late"] += count
            elif status == "VANG":
                weekly_dict[date_label]["absent"] += count

        weekly_trend = []
        for date_label, info in reversed(list(weekly_dict.items())):
            tot = info["present"] + info["late"] + info["absent"]
            rate = (
                round(((info["present"] + info["late"]) / tot * 100), 1)
                if tot > 0
                else 0.0
            )
            weekly_trend.append({
                "week": date_label,
                "rate": rate,
                "students": tot
            })
        if not weekly_trend:
            weekly_trend = [
                {"week": "T2", "rate": 0.0, "students": 0},
                {"week": "T3", "rate": 0.0, "students": 0}
            ]

        # 5. monthly_comparison
        monthly_comparison = [
            {"month": "T2", "thisYear": 89.2, "lastYear": 86.1},
            {"month": "T3", "thisYear": 90.1, "lastYear": 87.3},
            {"month": "T4", "thisYear": 87.8, "lastYear": 84.9},
            {"month": "T5", "thisYear": 91.2, "lastYear": 88.0},
        ]

        # 6. top_absent_students
        statement_absent = (
            select(Student, func.count(Attendance.attendance_id))
            .join(Attendance, Attendance.student_id == Student.student_id)
            .where(Attendance.status == "VANG")
            .group_by(Student.student_id)
            .order_by(func.count(Attendance.attendance_id).desc())
            .limit(5)
        )
        absent_results = self.session.exec(statement_absent).all()
        top_absent_students = []
        for student, absent_count in absent_results:
            major = self.session.get(Major, student.major_id) if student.major_id else None
            total_attendance_count = (
                self.session.exec(
                    select(func.count(Attendance.attendance_id)).where(
                        Attendance.student_id == student.student_id
                    )
                ).first()
                or 1
            )
            rate = round(((total_attendance_count - absent_count) / total_attendance_count * 100), 1)
            top_absent_students.append({
                "id": f"STUDENT{student.student_id:03d}",
                "name": f"{student.last_name} {student.first_name}".strip(),
                "department": major.major_name if major else "CNTT",
                "absences": absent_count,
                "rate": rate
            })

        # 7. class_performance
        statement_class = (
            select(ClassSection, Course, Attendance.status, func.count(Attendance.attendance_id))
            .join(Course, Course.course_id == ClassSection.course_id)
            .join(ClassSession, ClassSession.class_session_id == ClassSection.class_section_id)
            .join(Attendance, Attendance.class_session_id == ClassSession.class_session_id)
            .group_by(ClassSection.class_section_id, Course.course_id, Attendance.status)
        )
        class_results = self.session.exec(statement_class).all()
        class_map = {}
        for class_section, course, status, count in class_results:
            class_name = f"{course.course_name} ({class_section.class_section_id})"
            if class_name not in class_map:
                class_map[class_name] = {"present": 0, "absent": 0, "late": 0}
            if status == "CO_MAT":
                class_map[class_name]["present"] += count
            elif status == "VANG":
                class_map[class_name]["absent"] += count
            elif status in ["DI_MUON", "MUON"]:
                class_map[class_name]["late"] += count

        class_performance = []
        for name, info in class_map.items():
            tot = info["present"] + info["absent"] + info["late"]
            average_rate = round(
                ((info["present"] + info["late"]) / tot * 100), 1
            ) if tot > 0 else 0.0
            studs = self.session.exec(
                select(func.count(CourseRegistration.student_id))
                .where(
                    CourseRegistration.class_section_id
                    == int(name.split("(")[-1].replace(")", ""))
                )
            ).first() or 0
            class_performance.append({
                "class": name.split(" (")[0],
                "students": studs,
                "avgRate": average_rate,
                "trend": "up" if average_rate >= 80 else "down"
            })

        return {
            "summary": {
                "total_students": total_students,
                "avg_attendance_rate": avg_rate,
                "total_sessions": total_sessions,
                "attendance_warnings": attendance_warnings
            },
            "attendanceByDepartment": attendance_by_department,
            "statusDistribution": status_distribution,
            "weeklyTrend": weekly_trend,
            "monthlyComparison": monthly_comparison,
            "topAbsentStudents": top_absent_students,
            "classPerformance": class_performance
        }


def get_dashboard_service(session: Session = Depends(get_db)) -> DashboardService:
    """Dependency provider for DashboardService."""
    return DashboardService(session)
