# Rename Mapping

| Tên hiện tại | Tên mới | Giải thích |
|---|---|---|
| `app/api/routes/anhkhuonmat.py` | `app/api/routes/face_images.py` | Module route ảnh khuôn mặt, tên English snake_case. |
| `app/api/routes/baocao.py` | `app/api/routes/reports.py` | Module báo cáo, tên English số nhiều theo resource. |
| `app/api/routes/buoihoc.py` | `app/api/routes/class_sessions.py` | Buổi học tương ứng class sessions. |
| `app/api/routes/canbo.py` | `app/api/routes/staff.py` | Cán bộ tương ứng staff. |
| `app/api/routes/canhbaohoc_tap.py` | `app/api/routes/academic_warnings.py` | Cảnh báo học tập tương ứng academic warnings. |
| `app/api/routes/dangkyhocphan.py` | `app/api/routes/course_registrations.py` | Đăng ký học phần tương ứng course registrations. |
| `app/api/routes/diemdanh.py` | `app/api/routes/attendance.py` | Điểm danh tương ứng attendance. |
| `app/api/routes/hethong.py` | `app/api/routes/system.py` | Hệ thống tương ứng system. |
| `app/api/routes/hocphan.py` | `app/api/routes/courses.py` | Học phần tương ứng courses. |
| `app/api/routes/ketnoi_router.py` | `app/api/routes/webrtc_router.py` | Router xử lý WebRTC/connection. |
| `app/api/routes/khieunai.py` | `app/api/routes/appeals.py` | Khiếu nại tương ứng appeals. |
| `app/api/routes/lichhoc.py` | `app/api/routes/schedules.py` | Lịch học tương ứng schedules. |
| `app/api/routes/lophocphan.py` | `app/api/routes/class_sections.py` | Lớp học phần tương ứng class sections. |
| `app/api/routes/nganh.py` | `app/api/routes/majors.py` | Ngành tương ứng majors. |
| `app/api/routes/sinhvien.py` | `app/api/routes/students.py` | Sinh viên tương ứng students. |
| `app/api/routes/thoikhoabieu.py` | `app/api/routes/timetables.py` | Thời khóa biểu tương ứng timetables. |
| `app/api/routes/LUONGROUTER.md` | `app/api/routes/router_flow.md` | Tài liệu luồng router, snake_case. |
| `app/crud/buoihoc_crud.py` | `app/crud/class_session_crud.py` | CRUD cho class session. |
| `app/crud/canbo_crud.py` | `app/crud/staff_crud.py` | CRUD cho staff. |
| `app/crud/canhbaohoc_tap_crud.py` | `app/crud/academic_warning_crud.py` | CRUD cảnh báo học tập. |
| `app/crud/dangkyhocphan_crud.py` | `app/crud/course_registration_crud.py` | CRUD đăng ký học phần. |
| `app/crud/diemdanh_crud.py` | `app/crud/attendance_crud.py` | CRUD điểm danh. |
| `app/crud/diemdanh_summary_crud.py` | `app/crud/attendance_stats_crud.py` | Tránh trùng với attendance summary hiện có. |
| `app/crud/hocphan_crud.py` | `app/crud/course_crud.py` | CRUD học phần/course. |
| `app/crud/khieunai_crud.py` | `app/crud/appeal_crud.py` | CRUD khiếu nại. |
| `app/crud/lichday_crud.py` | `app/crud/teaching_schedule_crud.py` | Lịch dạy tương ứng teaching schedule. |
| `app/crud/lichhoc_crud.py` | `app/crud/student_schedule_crud.py` | Lịch học sinh viên. |
| `app/crud/lophocphan_crud.py` | `app/crud/class_section_crud.py` | CRUD lớp học phần. |
| `app/crud/nganh_crud.py` | `app/crud/major_crud.py` | CRUD ngành học. |
| `app/crud/sinhvien_crud.py` | `app/crud/student_crud.py` | CRUD sinh viên. |
| `app/crud/taikhoan_crud.py` | `app/crud/account_crud.py` | CRUD tài khoản. |
| `app/crud/thoikhoabieu_crud.py` | `app/crud/timetable_crud.py` | CRUD thời khóa biểu. |
| `app/models/anhdiemdanh.py` | `app/models/attendance_image.py` | Model ảnh điểm danh. |
| `app/models/anhkhuonmat.py` | `app/models/face_image.py` | Model ảnh khuôn mặt. |
| `app/models/buoihoc.py` | `app/models/class_session.py` | Model buổi học. |
| `app/models/canbo.py` | `app/models/staff.py` | Model cán bộ. |
| `app/models/canhbaohoc_tap.py` | `app/models/academic_warning.py` | Schema cảnh báo học tập. |
| `app/models/dangkyhocphan.py` | `app/models/course_registration.py` | Model đăng ký học phần. |
| `app/models/diemdanh.py` | `app/models/attendance.py` | Model điểm danh. |
| `app/models/diemdanh_summary.py` | `app/models/attendance_statistics.py` | Schema thống kê điểm danh. |
| `app/models/hocphan.py` | `app/models/course.py` | Model học phần/course. |
| `app/models/khieunai.py` | `app/models/appeal.py` | Model khiếu nại. |
| `app/models/lichday.py` | `app/models/teaching_schedule.py` | Schema lịch dạy. |
| `app/models/lichhoc.py` | `app/models/student_schedule.py` | Schema lịch học sinh viên. |
| `app/models/lophocphan.py` | `app/models/class_section.py` | Model lớp học phần. |
| `app/models/nganh.py` | `app/models/major.py` | Model ngành học. |
| `app/models/sinhvien.py` | `app/models/student.py` | Model sinh viên. |
| `app/models/taikhoan.py` | `app/models/account.py` | Model tài khoản. |
| `app/models/thoikhoabieu.py` | `app/models/timetable.py` | Model thời khóa biểu. |
| `app/services/canhbaohoc_tap_service.py` | `app/services/academic_warning_service.py` | Service cảnh báo học tập. |
| `app/services/diemdanh_summary_service.py` | `app/services/attendance_stats_service.py` | Service thống kê điểm danh. |
| `app/services/khieunai_service.py` | `app/services/appeal_service.py` | Service khiếu nại. |
| `app/services/lichhoc_service.py` | `app/services/student_schedule_service.py` | Service lịch học sinh viên. |
| `app/services/face_dectection.py` | `app/services/face_detection.py` | Sửa typo `dectection`. |
| `app/utils/create_ebedding_faiss.py` | `app/utils/create_embedding_faiss.py` | Sửa typo `ebedding`. |
| `app/frontend/pages/super-admin.py` | `app/frontend/pages/super_admin.py` | Bỏ dấu gạch ngang, dùng snake_case. |
| `tests/canbo/` | `tests/staff/` | Test folder theo resource English. |
| `tests/canhbaohoc_tap/` | `tests/academic_warnings/` | Test folder theo resource English. |
| `tests/diemdanh/` | `tests/attendance/` | Test folder theo resource English. |
| `tests/khieunai/` | `tests/appeals/` | Test folder theo resource English. |
| `tests/lichhoc/` | `tests/schedules/` | Test folder theo resource English. |
| `tests/sinhvien/` | `tests/students/` | Test folder theo resource English. |
| `tests/integration_test_luong_chinh.py` | `tests/test_main_flow.py` | Tên test English, ngắn gọn. |
| `tests/staff/test_canbo_router.py` | `tests/staff/test_staff_router.py` | Test router staff. |
| `tests/academic_warnings/test_canhbaohoc_tap_router.py` | `tests/academic_warnings/test_academic_warnings_router.py` | Test router academic warnings. |
| `tests/attendance/test_diemdanh_summary_router.py` | `tests/attendance/test_attendance_stats_router.py` | Test thống kê attendance. |
| `tests/appeals/test_khieunai_router.py` | `tests/appeals/test_appeals_router.py` | Test router appeals. |
| `tests/appeals/test_khieunai_service.py` | `tests/appeals/test_appeal_service.py` | Test appeal service. |
| `tests/schedules/test_lichhoc_router.py` | `tests/schedules/test_schedules_router.py` | Test schedules router. |
| `tests/students/test_sinhvien_router.py` | `tests/students/test_students_router.py` | Test students router. |
| `frontend-design/` | `frontend_design/` | Bỏ dấu gạch ngang, dùng snake_case. |
| `PLAN_CAN_LAM.md` | `action_plan.md` | Tên tài liệu English snake_case. |
| `DATABASE.md` | `database.md` | Tên tài liệu snake_case/lowercase. |
| `FASTAPI_ROUTER_REFACTOR_PROGRESS.md` | `fastapi_router_refactor_progress.md` | Tên tài liệu snake_case/lowercase. |
| `PEP8_CHANGE_SUMMARY.md` | `pep8_change_summary.md` | Tên tài liệu snake_case/lowercase. |
| `PEP8_NAMING_CHANGE_SUMMARY.md` | `pep8_naming_change_summary.md` | Tên tài liệu snake_case/lowercase. |
| `PEP257_CHANGE_SUMMARY.md` | `pep257_change_summary.md` | Tên tài liệu snake_case/lowercase. |
| `ASYNC_MIGRATION_PROGRESS.md` | `async_migration_progress.md` | Tên tài liệu snake_case/lowercase. |
| `ASYNC_ROUTES_AUDIT.md` | `async_routes_audit.md` | Tên tài liệu snake_case/lowercase. |
| `PRIORITY_1_COMPLETE.md` | `priority_1_complete.md` | Tên tài liệu snake_case/lowercase. |
| `PYDANTIC_AUDIT.md` | `pydantic_audit.md` | Tên tài liệu snake_case/lowercase. |
| `XÁC ĐỊNH YÊU CẦU HỆ THỐNG(đã sửa).docx` | `system_requirements_revised.docx` | Bỏ dấu, khoảng trắng, ký tự đặc biệt. |
| `app` | Không cần đổi | Thư mục chuẩn FastAPI/Python. |
| `app/api` | Không cần đổi | Thư mục chuẩn API layer. |
| `app/services` | Không cần đổi | Thư mục chuẩn service layer. |
| `app/models` | Không cần đổi | Thư mục chuẩn model/schema layer. |
| `app/core` | Không cần đổi | Thư mục chuẩn core config. |
| `app/middleware` | Không cần đổi | Thư mục chuẩn middleware. |
| `app/utils` | Không cần đổi | Thư mục chuẩn utilities. |
| `tests` | Không cần đổi | Thư mục chuẩn test suite. |
| `app/alembic` | Không cần đổi | Thư mục migration hiện hữu. |
| `README.md` | Không cần đổi | Tên tài liệu chuẩn phổ biến. |
| `Dockerfile` | Không cần đổi | Tên chuẩn Docker. |
| `docker-compose.yml` | Không cần đổi | Tên chuẩn Docker Compose. |
| `uploads/` | Không cần đổi | Dữ liệu runtime, không đổi để tránh mất liên kết file. |
| `dataset/` | Không cần đổi | Dữ liệu mẫu/runtime, không đổi để tránh mất liên kết file. |
| `venv/` | Không cần đổi | Virtual environment, không thuộc source naming. |

## API Route Slugs And Tags

| Tên hiện tại | Tên mới | Giải thích |
|---|---|---|
| `/anh-khuon-mat`, tag `anh-khuon-mat` | `/face-images`, tag `face-images` | Endpoint quản lý ảnh khuôn mặt, dùng resource English số nhiều. |
| `/bao-cao`, tag `bao-cao` | `/reports`, tag `reports` | Endpoint báo cáo, tên ngắn gọn theo resource. |
| `/buoi-hoc`, tag `buoi-hoc` | `/class-sessions`, tag `class-sessions` | Buổi học tương ứng class sessions trong ngữ cảnh lớp học. |
| `/canbo`, tag `canbo` | `/staff`, tag `staff` | Cán bộ tương ứng staff. |
| `/canh-bao-hoc-tap`, tag `canh-bao-hoc-tap` | `/academic-warnings`, tag `academic-warnings` | Cảnh báo học tập tương ứng academic warnings. |
| `/dangkyhocphan`, tag `dangkyhocphan` | `/course-registrations`, tag `course-registrations` | Đăng ký học phần tương ứng course registrations. |
| `/diem-danh`, tag `diem-danh` | `/attendance`, tag `attendance` | Điểm danh tương ứng attendance. |
| `/he-thong`, tag `he-thong` | `/system`, tag `system` | Endpoint hệ thống, tên English rõ nghĩa. |
| `/hocphan`, tag `hocphan` | `/courses`, tag `courses` | Học phần tương ứng courses. |
| `/khieu-nai`, tag `khieu-nai` | `/appeals`, tag `appeals` | Khiếu nại tương ứng appeals. |
| `/lich-hoc`, tag `lich-hoc` | `/schedules`, tag `schedules` | Lịch học tương ứng schedules. |
| `/lop-hoc-phan`, tag `lop-hoc-phan` | `/class-sections`, tag `class-sections` | Lớp học phần tương ứng class sections. |
| `/nganh`, tag `nganh` | `/majors`, tag `majors` | Ngành học tương ứng majors. |
| `/sinh-vien`, tag `sinh-vien` | `/students`, tag `students` | Sinh viên tương ứng students. |
| `/thoikhoabieu`, tag `thoikhoabieu` | `/timetables`, tag `timetables` | Thời khóa biểu tương ứng timetables. |
| `/buoi-hoc/{id}/mo-diem-danh` | `/class-sessions/{id}/open-attendance` | Subpath thao tác điểm danh chuyển sang verb phrase English. |
| `/buoi-hoc/{id}/dong-diem-danh` | `/class-sessions/{id}/close-attendance` | Subpath thao tác điểm danh chuyển sang verb phrase English. |
| `/buoi-hoc/{id}/diem-danh` | `/class-sessions/{id}/attendance` | Sub-resource attendance dùng English. |
| `/attendance/tu-dong` | `/attendance/automatic` | Chế độ điểm danh tự động dùng English. |
| `/attendance/thu-cong` | `/attendance/manual` | Chế độ điểm danh thủ công dùng English. |
| `/lop-hoc-phan/{id}/sinh-vien` | `/class-sections/{id}/students` | Sub-resource students dùng English số nhiều. |
| `/lop-hoc-phan/{id}/thong-ke` | `/class-sections/{id}/statistics` | Sub-resource statistics dùng English. |
| `/lop-hoc-phan/{id}/canh-bao` | `/class-sections/{id}/warnings` | Sub-resource warnings dùng English. |
