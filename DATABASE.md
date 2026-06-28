# Tài liệu Tài liệu Cấu trúc Cơ sở Dữ liệu (Database Schema Documentation)

Hệ thống Điểm danh Tự động sử dụng Cơ sở dữ liệu **PostgreSQL** trên Cloud (Render) với kiến trúc chuẩn **RESTful API** Tiếng Anh (`snake_case`). Tất cả các bảng dữ liệu cũ đã được chuyển sổ và đồng bộ 100% sang chuẩn mới.

---

## Danh sách các Bảng Dữ liệu (Database Tables)

### 1. `accounts` (Tài khoản Hệ thống)
Lưu trữ thông tin xác thực đăng nhập của tất cả các người dùng (Sinh viên, Cán bộ, Giảng viên, Admin).

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `account_id` | `INTEGER` | **PK**, Auto-increment | Mã định danh duy nhất của tài khoản. |
| `username` | `VARCHAR(50)` | UNIQUE, NOT NULL, Index | Tên đăng nhập (MSSV đối với sinh viên, Mã CB đối với cán bộ/giảng viên). |
| `password_hash` | `VARCHAR(255)` | NOT NULL | Mật khẩu đã mã hóa Bcrypt. |
| `role` | `VARCHAR(20)` | NOT NULL | Vai trò (`SINH_VIEN`, `GIANG_VIEN`, `CAN_BO`, `ADMIN`). |
| `status` | `BOOLEAN` | DEFAULT `true` | Trạng thái hoạt động của tài khoản (`true`: Hoạt động, `false`: Khóa). |
| `failed_login_count` | `INTEGER` | DEFAULT `0` | Số lần đăng nhập sai mật khẩu liên tiếp. |
| `locked_until` | `TIMESTAMP` | NULL | Thời điểm tài khoản hết bị tạm khóa (khóa 15 phút nếu sai >5 lần). |
| `last_login_at` | `TIMESTAMP` | NULL | Thời điểm đăng nhập thành công gần nhất. |
| `created_at` | `TIMESTAMP` | DEFAULT `NOW()` | Thời gian tạo tài khoản. |

---

### 2. `students` (Hồ sơ Sinh viên)
Lưu trữ thông tin cá nhân và học tập của sinh viên.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `student_id` | `INTEGER` | **PK** | Mã số sinh viên (MSSV). |
| `first_name` | `VARCHAR(50)` | NOT NULL | Tên sinh viên. |
| `last_name` | `VARCHAR(50)` | NOT NULL | Họ và tên đệm sinh viên. |
| `birth_date` | `DATE` | NULL | Ngày tháng năm sinh. |
| `gender` | `VARCHAR(10)` | NULL | Giới tính (`Nam`, `Nữ`, `Khác`). |
| `phone` | `VARCHAR(15)` | NULL | Số điện thoại liên lạc. |
| `google_email` | `VARCHAR(100)` | NULL | Email Google trường cấp dùng cho đăng nhập OAuth. |
| `major_id` | `INTEGER` | **FK** -> `majors.major_id` | Chuyên ngành học của sinh viên. |
| `account_id` | `INTEGER` | **FK** -> `accounts.account_id` | Tài khoản đăng nhập tương ứng. |
| `academic_status` | `VARCHAR(30)` | DEFAULT `'DANG_HOC'` | Trạng thái học tập (`DANG_HOC`, `THOI_HOC`, `GRADUATED`). |
| `study_started_at` | `DATE` | NULL | Ngày nhập học. |

---

### 3. `staff` (Hồ sơ Cán bộ & Giảng viên)
Lưu trữ thông tin cán bộ quản lý và giảng viên giảng dạy.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `staff_id` | `INTEGER` | **PK** | Mã cán bộ / giảng viên. |
| `first_name` | `VARCHAR(50)` | NOT NULL | Tên cán bộ/giảng viên. |
| `last_name` | `VARCHAR(50)` | NOT NULL | Họ và tên đệm. |
| `phone` | `VARCHAR(15)` | NULL | Số điện thoại liên lạc. |
| `gender` | `VARCHAR(10)` | NULL | Giới tính. |
| `birth_date` | `DATE` | NULL | Ngày sinh. |
| `google_email` | `VARCHAR(100)` | NULL | Email Google công vụ. |
| `account_id` | `INTEGER` | **FK** -> `accounts.account_id` | Tài khoản đăng nhập tương ứng. |
| `position` | `VARCHAR(100)` | NULL | Chức vụ / Học vị (Giảng viên, Trưởng khoa,...). |
| `status` | `BOOLEAN` | DEFAULT `true` | Trạng thái công tác (`true`: Đang làm việc). |

---

### 4. `courses` (Danh mục Học phần / Môn học)
Quản lý các môn học trong chương trình đào tạo.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `course_id` | `INTEGER` | **PK**, Auto-increment | Mã định danh học phần. |
| `course_name` | `VARCHAR(100)` | NOT NULL | Tên môn học / học phần. |
| `description` | `TEXT` | NULL | Mô tả chi tiết môn học. |
| `credit_count` | `INTEGER` | NOT NULL | Số tín chỉ của môn học. |
| `status` | `BOOLEAN` | DEFAULT `true` | Trạng thái môn học (`true`: Đang giảng dạy). |

---

### 5. `class_sections` (Lớp Học phần)
Quản lý các lớp học phần được mở trong từng học kỳ.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `class_section_id` | `INTEGER` | **PK**, Auto-increment | Mã định danh lớp học phần. |
| `course_id` | `INTEGER` | **FK** -> `courses.course_id` | Môn học tương ứng. |
| `staff_id` | `INTEGER` | **FK** -> `staff.staff_id` | Giảng viên phụ trách giảng dạy. |
| `semester` | `VARCHAR(10)` | NOT NULL | Học kỳ (HK1, HK2, HK3). |
| `academic_year` | `VARCHAR(20)` | NOT NULL | Năm học (ví dụ: 2025-2026). |
| `minimum_attendance_rate` | `FLOAT` | DEFAULT `0.8` | Tỷ lệ chuyên cần tối thiểu bắt buộc (ví dụ: 80%). |
| `status` | `BOOLEAN` | DEFAULT `true` | Trạng thái lớp học phần. |
| `created_at` | `TIMESTAMP` | DEFAULT `NOW()` | Thời gian tạo lớp. |

---

### 6. `class_sessions` (Các Buổi học Điểm danh)
Quản lý chi tiết từng buổi học cụ thể của lớp học phần.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `class_session_id` | `INTEGER` | **PK**, Auto-increment | Mã định danh buổi học. |
| `class_section_id` | `INTEGER` | **FK** -> `class_sections.class_section_id` | Thuộc lớp học phần nào. |
| `class_date` | `DATE` | NOT NULL | Ngày diễn ra buổi học. |
| `start_time` | `TIME` | NOT NULL | Giờ bắt đầu điểm danh. |
| `end_time` | `TIME` | NOT NULL | Giờ kết thúc điểm danh. |
| `session_number` | `INTEGER` | NOT NULL | Thứ tự buổi học (Buổi 1, Buổi 2,...). |
| `status` | `VARCHAR(20)` | DEFAULT `'COMPLETED'` | Trạng thái buổi học (`SCHEDULED`, `ONGOING`, `COMPLETED`). |
| `recognition_threshold` | `FLOAT` | DEFAULT `0.6` | Ngưỡng độ tin cậy nhận diện AI khuôn mặt (0.6 - 0.8). |
| `late_grace_minutes` | `INTEGER` | DEFAULT `15` | Số phút đi muộn cho phép (sau phút này tính là Vắng). |
| `note` | `TEXT` | NULL | Ghi chú thêm của giảng viên cho buổi học. |

---

### 7. `attendance` (Kết quả Điểm danh)
Lưu trữ trạng thái và chi tiết điểm danh của sinh viên trong từng buổi học.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `attendance_id` | `INTEGER` | **PK**, Auto-increment | Mã bản ghi điểm danh. |
| `student_id` | `INTEGER` | **FK** -> `students.student_id` | Sinh viên được điểm danh. |
| `class_session_id` | `INTEGER` | **FK** -> `class_sessions.class_session_id` | Buổi học tương ứng. |
| `status` | `VARCHAR(20)` | NOT NULL | Trạng thái điểm danh (`PRESENT`: Có mặt, `ABSENT`: Vắng, `LATE`: Đi muộn). |
| `method` | `VARCHAR(30)` | DEFAULT `'FACE_RECOGNITION'` | Phương thức điểm danh (`FACE_RECOGNITION`, `MANUAL_TEACHER`, `QR_CODE`). |
| `confidence` | `FLOAT` | NULL | Độ tin cậy nhận diện khuôn mặt của AI (0.0 đến 1.0). |
| `attendance_time` | `TIMESTAMP` | NULL | Thời điểm thực hiện điểm danh thành công. |
| `edit_reason` | `TEXT` | NULL | Lý do điều chỉnh điểm danh (nếu giảng viên sửa tay). |

---

### 8. `face_images` (Bộ dữ liệu Khuôn mặt AI)
Lưu trữ đường dẫn ảnh và vector đặc trưng (Embeddings) phục vụ AI nhận diện khuôn mặt.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `image_id` | `INTEGER` | **PK**, Auto-increment | Mã ảnh khuôn mặt. |
| `student_id` | `INTEGER` | **FK** -> `students.student_id` | Sinh viên sở hữu ảnh. |
| `image_path` | `VARCHAR(255)` | NOT NULL | Đường dẫn lưu trữ tệp ảnh trên máy chủ. |
| `image_type` | `VARCHAR(20)` | DEFAULT `'REGISTRATION'` | Loại ảnh (`REGISTRATION`: Ảnh đăng ký mẫu, `ATTENDANCE`: Ảnh chụp điểm danh). |
| `quality_score` | `FLOAT` | DEFAULT `1.0` | Điểm chất lượng ảnh (ánh sáng, góc mặt, độ nét). |
| `review_status` | `VARCHAR(20)` | DEFAULT `'APPROVED'` | Trạng thái duyệt ảnh (`PENDING`, `APPROVED`, `REJECTED`). |
| `rejection_reason` | `TEXT` | NULL | Lý do từ chối ảnh (nếu ảnh quá mờ hoặc không rõ mặt). |
| `reviewed_at` | `TIMESTAMP` | NULL | Thời gian kiểm duyệt ảnh. |
| `reviewer_id` | `INTEGER` | NULL | Cán bộ kiểm duyệt ảnh. |
| `embedding_vector` | `TEXT / JSON` | NULL | Chuỗi vector 512 chiều trích xuất bởi Deep Learning (InsightFace/FaceNet). |

---

### 9. `otp_codes` (Mã Xác thực OTP)
Lưu trữ mã OTP gửi qua Email trường để xác thực đăng ký tài khoản.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `otp_id` | `INTEGER` | **PK**, Auto-increment | Mã bản ghi OTP. |
| `email` | `VARCHAR(100)` | NOT NULL, Index | Email nhận mã OTP. |
| `code` | `VARCHAR(6)` | NOT NULL | Mã OTP ngẫu nhiên 6 chữ số. |
| `expires_at` | `TIMESTAMP` | NOT NULL | Thời điểm hết hạn của mã OTP (hiệu lực 5 phút). |
| `is_used` | `BOOLEAN` | DEFAULT `false` | Đã sử dụng mã OTP để kích hoạt tài khoản chưa. |
| `created_at` | `TIMESTAMP` | DEFAULT `NOW()` | Thời gian khởi tạo mã OTP. |

---

### 10. `refresh_token` (Phiên Đăng nhập Dài hạn)
Lưu trữ token mã hóa phục vụ tính năng "Ghi nhớ đăng nhập" (Remember Me).

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `refresh_token_id` | `INTEGER` | **PK**, Auto-increment | Mã bản ghi phiên đăng nhập. |
| `account_id` | `INTEGER` | **FK** -> `accounts.account_id` | Tài khoản sử dụng phiên đăng nhập này. |
| `token_hash` | `VARCHAR(255)` | UNIQUE, NOT NULL | Mã hash bảo mật của Refresh Token. |
| `expires_at` | `TIMESTAMP` | NOT NULL | Thời điểm hết hạn của Refresh Token (ví dụ 30 ngày). |
| `created_at` | `TIMESTAMP` | DEFAULT `NOW()` | Thời điểm tạo phiên. |
| `last_used_at` | `TIMESTAMP` | NULL | Thời điểm vừa sử dụng Refresh Token để lấy Access Token mới. |
| `revoked_at` | `TIMESTAMP` | NULL | Thời điểm phiên bị hủy (khi thu hồi hoặc đăng xuất). |
| `user_agent` | `VARCHAR(255)` | NULL | Trình duyệt và thiết bị người dùng sử dụng. |
| `ip_address` | `VARCHAR(45)` | NULL | Địa chỉ IP của người dùng. |

---

### 11. `auditlog` (Nhật ký Hệ thống)
Ghi lại toàn bộ thao tác quan trọng (Đăng nhập, Đăng ký, Điểm danh, Đổi mật khẩu) để kiểm vết an ninh.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `audit_log_id` | `INTEGER` | **PK**, Auto-increment | Mã bản ghi nhật ký. |
| `account_id` | `INTEGER` | **FK** -> `accounts.account_id` | Người thực hiện thao tác (NULL nếu chưa đăng nhập). |
| `role` | `VARCHAR(20)` | NULL | Vai trò của người thực hiện thao tác. |
| `action` | `VARCHAR(100)` | NOT NULL | Hành động (`DANG_NHAP`, `DANG_KY`, `DIEM_DANH`,...). |
| `target_type` | `VARCHAR(100)` | NULL | Đối tượng bị tác động (`Account`, `Student`, `Attendance`). |
| `target_id` | `VARCHAR(100)` | NULL | ID của đối tượng bị tác động. |
| `before_data` | `JSON` | NULL | Dữ liệu trước khi thay đổi. |
| `after_data` | `JSON` | NULL | Dữ liệu sau khi thay đổi. |
| `ip` | `VARCHAR(45)` | NULL | Địa chỉ IP gửi yêu cầu. |
| `user_agent` | `VARCHAR(255)` | NULL | Thông tin thiết bị/trình duyệt. |
| `status` | `VARCHAR(30)` | DEFAULT `'SUCCESS'` | Trạng thái hành động (`SUCCESS`, `FAILED`). |
| `detail` | `VARCHAR(500)` | NULL | Chi tiết kết quả hoặc nguyên nhân lỗi. |
| `timestamp` | `TIMESTAMP` | DEFAULT `NOW()` | Thời điểm ghi nhật ký. |

---

### 12. `majors` (Danh mục Ngành học)
Lưu trữ danh sách các ngành/khoa đào tạo trong nhà trường.

| Tên trường (Column) | Kiểu dữ liệu (Type) | Ràng buộc (Constraint) | Mô tả chi tiết |
| :--- | :--- | :--- | :--- |
| `major_id` | `INTEGER` | **PK**, Auto-increment | Mã định danh ngành học. |
| `major_name` | `VARCHAR(100)` | NOT NULL | Tên ngành học (Công nghệ thông tin, Kế toán,...). |
| `description` | `TEXT` | NULL | Mô tả thêm về ngành học. |
