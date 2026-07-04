from app.crud.academic_warning_crud import get_absence_warning_sources_by_student
from app.crud.account_crud import (
    authenticate_account,
    create_account,
    create_user,
    get_account_by_profile_email,
    get_account_by_profile_google_email,
    get_account_by_username,
    get_account_profile,
    get_user_by_email,
    update_account,
    update_user,
)
from app.crud.appeal_crud import (
    count_actionable_appeals_by_staff,
    count_pending_appeals_by_staff,
    get_actionable_appeal_detail_by_staff,
    get_actionable_appeals_by_staff,
    update_appeal_resolution,
)
from app.crud.attendance_stats_crud import (
    get_attendance_semester_counts_by_student,
)
from app.crud.attendance_summary_crud import get_attendance_counts_for_teacher
from app.crud.oauth_identity_crud import (
    create_oauth_identity,
    get_oauth_identity_by_provider_subject,
    update_oauth_identity_last_login,
)
from app.crud.refresh_token_crud import (
    create_refresh_token,
    get_refresh_token_by_hash,
    revoke_all_refresh_tokens_for_account,
    revoke_refresh_token,
    update_refresh_token_last_used,
)
from app.crud.staff_crud import (
    create_staff_member,
    delete_staff_member,
    get_staff_member,
    get_staff_member_by_account_id,
    get_staff_member_by_google_email,
    get_staff_members,
    update_staff_member,
)
from app.crud.student_crud import (
    create_student,
    delete_student,
    get_student,
    get_student_by_account_id,
    get_student_by_google_email,
    get_students,
    update_student,
)
from app.crud.student_schedule_crud import get_today_schedule_by_student
from app.crud.teaching_schedule_crud import (
    count_current_teaching_class_sections_by_staff_member,
    get_recent_lessons_by_staff_member,
    get_teaching_schedule_by_staff_member,
)

__all__ = [
    "authenticate",
    "authenticate_account",
    "create_account",
    "create_staff_member",
    "create_oauth_identity",
    "create_refresh_token",
    "create_student",
    "create_user",
    "delete_staff_member",
    "delete_student",
    "get_staff_member",
    "get_staff_member_by_account_id",
    "get_staff_member_by_google_email",
    "get_staff_members",
    "get_recent_lessons_by_staff_member",
    "count_current_teaching_class_sections_by_staff_member",
    "count_actionable_appeals_by_staff",
    "count_pending_appeals_by_staff",
    "get_attendance_counts_for_teacher",
    "get_attendance_semester_counts_by_student",
    "get_actionable_appeals_by_staff",
    "get_actionable_appeal_detail_by_staff",
    "get_teaching_schedule_by_staff_member",
    "get_today_schedule_by_student",
    "get_account_by_profile_email",
    "get_account_by_profile_google_email",
    "get_account_by_username",
    "get_account_profile",
    "get_absence_warning_sources_by_student",
    "get_oauth_identity_by_provider_subject",
    "get_refresh_token_by_hash",
    "get_student",
    "get_student_by_account_id",
    "get_student_by_google_email",
    "get_students",
    "get_user_by_email",
    "revoke_all_refresh_tokens_for_account",
    "revoke_refresh_token",
    "update_account",
    "update_staff_member",
    "update_appeal_resolution",
    "update_oauth_identity_last_login",
    "update_refresh_token_last_used",
    "update_student",
    "update_user",
]
