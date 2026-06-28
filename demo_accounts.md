# Danh sách Tài khoản & Dữ liệu Mẫu Thử nghiệm Hệ thống (Demo Accounts & Credentials)

Tài liệu này lưu trữ danh sách tất cả các tài khoản thử nghiệm và dữ liệu mẫu đã được khởi tạo trong Cơ sở dữ liệu PostgreSQL (`dbdiemdanh`) phục vụ kiểm thử và demo ứng dụng.

---

## 🔑 1. Danh sách Tài khoản Đăng nhập (Login Credentials)

| Vai trò (Role) | Tên đăng nhập / MSSV | Mật khẩu (Password) | Họ và Tên | Email liên kết | Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 👑 **ADMIN** | `admin` | `admin123456` | Quản trị viên | `admin@example.com` | Quyền quản trị tối cao toàn hệ thống. |
| 🎓 **SINH VIÊN** | `21080001` | `12345` | Nguyễn Đức Nghiêm | `nguyenducnghiemthptllqt@gmail.com` | **Tài khoản sinh viên thử nghiệm chính.** |
| 🎓 **SINH VIÊN** | `21080002` | `12345` | Trần Thị Mai | `maitt@example.com` | Sinh viên mẫu ngành KTPM. |
| 🎓 **SINH VIÊN** | `21080003` | `12345` | Lê Hoàng Nam | `namlh@example.com` | Sinh viên mẫu ngành HTTT. |
| 👨‍🏫 **GIẢNG VIÊN**| `gv2101` | `12345` | TS. Nguyễn Văn An | `nguyenvanan@example.com` | Giảng viên dạy môn Lập trình Web FastAPI. |
| 👨‍🏫 **GIẢNG VIÊN**| `gv2102` | `12345` | ThS. Trần Thị Bình | `tranthibinh@example.com` | Giảng viên dạy môn AI Nhận diện mặt. |

> 💡 **Lưu ý**: Bạn có thể sử dụng cả **Tên đăng nhập (MSSV/Mã CB)** hoặc **Email trường học** để đăng nhập vào hệ thống.

---

## 📚 2. Thống kê Dữ liệu Mẫu trong các Bảng (Seed Data Summary)

### 🏫 Môn học & Lớp học phần (`courses`, `class_sections`)

### 📩 Dữ liệu Mẫu Khiếu nại Chờ Xử lý (`appeals`)
- Đã khởi tạo **2 đơn khiếu nại mẫu ở trạng thái `CHO_XU_LY`** cho các sinh viên lớp Lập trình Web do **TS. Nguyễn Văn An** (`gv2101`) đảm nhận để thử nghiệm tính năng Duyệt/Từ chối khiếu nại điểm danh.
* **INT101**: Lập trình Web với Python FastAPI (3 tín chỉ) - Lớp `INT101_01` (GV: TS. Nguyễn Văn An, Phòng A2-301)
* **INT102**: Học máy & Nhận diện khuôn mặt AI (4 tín chỉ) - Lớp `INT102_01` (GV: ThS. Trần Thị Bình, Phòng B1-202)
* **INT103**: Cơ sở dữ liệu nâng cao (3 tín chỉ)

### 📋 Điểm danh & Buổi học (`class_sessions`, `attendance`)
* Buổi học Buổi 1 Lớp `INT101_01`: Sinh viên `21080001` Có mặt (`PRESENT`), SV `21080002` Đi muộn (`LATE`).
* Buổi học Buổi 1 Lớp `INT102_01`: Sinh viên `21080001` Có mặt (`PRESENT`), SV `21080003` Vắng (`ABSENT`).

### 🖼️ Khuôn mặt AI & Khiếu nại (`face_images`, `appeals`)
* **Ảnh mẫu AI**: Đã duyệt ảnh nhận diện mẫu cho cả 3 sinh viên (`APPROVED`).
* **Khiếu nại**: Sinh viên `21080003` có 1 đơn khiếu nại đang chờ xử lý (`PENDING`).
