from fastapi import APIRouter

from app.api.routes import (
    academic_warnings,
    appeals,
    attendance,
    class_sections,
    class_sessions,
    course_registrations,
    courses,
    face_images,
    google_auth_router,
    login,
    majors,
    reports,
    schedules,
    staff,
    students,
    system,
    system_router,
    timetables,
    user,
    webrtc_router,
)

api_router = APIRouter()
api_router.include_router(system_router.router)
api_router.include_router(webrtc_router.router)
api_router.include_router(google_auth_router.router)
api_router.include_router(user.router)
api_router.include_router(login.router)
api_router.include_router(staff.router)
api_router.include_router(academic_warnings.router)
api_router.include_router(attendance.router)
api_router.include_router(appeals.router)
api_router.include_router(students.router)
api_router.include_router(schedules.router)
api_router.include_router(class_sections.router)
api_router.include_router(class_sessions.router)
api_router.include_router(majors.router)
api_router.include_router(courses.router)
api_router.include_router(course_registrations.router)
api_router.include_router(timetables.router)
api_router.include_router(face_images.router)
api_router.include_router(face_images.verification_router)
api_router.include_router(reports.router)
api_router.include_router(system.router)
