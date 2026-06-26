# PEP 8 Naming Change Summary

This file documents the naming cleanup focused on PEP 8 compliance and English
identifiers.

## Package And Temporary Files

| Previous name | New name | Reason |
| --- | --- | --- |
| `app/AI_models` | `app/ai_models` | Package names should be lowercase. |
| `app/utils/tempCodeRunnerFile.py` | Removed | Temporary editor file, not project code. |
| `app/test/tempCodeRunnerFile.py` | Removed | Temporary editor file, not project code. |

## Internal Python Variables

The system report endpoint now uses English `snake_case` variables internally
while preserving the existing response JSON keys.

| Previous variable | New variable |
| --- | --- |
| `attendanceByDepartment` | `attendance_by_department` |
| `statusDistribution` | `status_distribution` |
| `weeklyTrend` | `weekly_trend` |
| `monthlyComparison` | `monthly_comparison` |
| `topAbsentStudents` | `top_absent_students` |
| `classPerformance` | `class_performance` |
| `avgRate` | `average_rate` |

## CRUD And Route Function Names

The following internal function names were renamed to English. URL paths and
JSON response keys were left unchanged to avoid breaking frontend contracts.

| Previous function | New function |
| --- | --- |
| `get_hocphan` | `get_course` |
| `get_hocphans` | `get_courses` |
| `create_hocphan` | `create_course` |
| `update_hocphan` | `update_course` |
| `delete_hocphan` | `delete_course` |
| `read_hocphan` | `read_course` |
| `read_hocphans` | `read_courses` |
| `get_nganh` | `get_major` |
| `get_nganhs` | `get_majors` |
| `create_nganh` | `create_major` |
| `update_nganh` | `update_major` |
| `delete_nganh` | `delete_major` |
| `read_nganh` | `read_major` |
| `read_nganhs` | `read_majors` |
| `get_dangkyhocphan` | `get_course_registration` |
| `get_dangkyhocphans` | `get_course_registrations` |
| `create_dangkyhocphan` | `create_course_registration` |
| `update_dangkyhocphan` | `update_course_registration` |
| `delete_dangkyhocphan` | `delete_course_registration` |
| `read_dangkyhocphan` | `read_course_registration` |
| `read_dangkyhocphans` | `read_course_registrations` |
| `get_sinh_vien` | `get_student` |
| `get_sinh_viens` | `get_students` |
| `get_sinh_vien_by_google_email` | `get_student_by_google_email` |
| `get_sinh_vien_by_account_id` | `get_student_by_account_id` |
| `create_sinh_vien` | `create_student` |
| `update_sinh_vien` | `update_student` |
| `delete_sinh_vien` | `delete_student` |
| `read_sinh_vien` | `read_student` |
| `read_sinh_viens` | `read_students` |
| `get_can_bo` | `get_staff_member` |
| `get_can_bos` | `get_staff_members` |
| `get_can_bo_by_google_email` | `get_staff_member_by_google_email` |
| `get_can_bo_by_account_id` | `get_staff_member_by_account_id` |
| `create_can_bo` | `create_staff_member` |
| `update_can_bo` | `update_staff_member` |
| `delete_can_bo` | `delete_staff_member` |
| `read_can_bo` | `read_staff_member` |
| `read_can_bos` | `read_staff_members` |
| `get_current_active_sinhvien` | `get_current_active_student` |
| `get_current_active_giangvien` | `get_current_active_lecturer` |
| `get_lich_hoc_hom_nay` | `get_today_schedule` |
| `get_lich_hoc_hom_nay_by_sinh_vien` | `get_today_schedule_by_student` |
| `read_lich_hoc_hom_nay_sinh_vien` | `read_today_student_schedule` |
| `get_lich_day_by_can_bo` | `get_teaching_schedule_by_staff_member` |
| `get_buoi_hoc_gan_day_by_can_bo` | `get_recent_lessons_by_staff_member` |
| `count_lop_hoc_phan_dang_day_by_can_bo` | `count_current_teaching_class_sections_by_staff_member` |
| `get_tong_buoi_co_mat_hoc_ky` | `get_semester_present_lesson_total` |
| `read_tong_buoi_co_mat_hoc_ky_sinh_vien` | `read_student_semester_present_lesson_total` |
| `tinh_trang_thai_diem_danh` | `calculate_attendance_status` |
| `diem_danh_tu_dong_lo` | `mark_attendance_by_lora` |
| `diem_danh_tu_dong` | `mark_attendance_automatically` |
| `diem_danh_thu_cong` | `mark_attendance_manually` |
| `chot_diem_danh_vang` | `finalize_absent_attendance` |
| `get_canh_bao_vang_by_sinh_vien` | `get_absence_warnings_by_student` |
| `read_canh_bao_vang_sinh_vien` | `read_student_absence_warnings` |

## Preserved Names

Database/model fields such as `ma_hoc_phan`, `ma_nganh`, and `ma_dang_ky` were
not renamed in this pass because they are tied to the database schema and
Pydantic models.

Public response keys such as `attendanceByDepartment`, `statusDistribution`,
and `avgRate` were also preserved because the frontend may depend on them.
