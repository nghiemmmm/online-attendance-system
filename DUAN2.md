# 🎓 Online Attendance System with AI Face Recognition
### Hệ thống Điểm danh & Nhận diện Khuôn mặt AI Trực tuyến

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Next.js 16](https://img.shields.io/badge/Next.js%2016-000000?style=for-the-badge&logo=next.js&logoColor=white)
![React 19](https://img.shields.io/badge/React%2019-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

---

## 🚀 Công nghệ & Kiến trúc Hệ thống (Technology Stack)

### 🤖 AI Core & Computer Vision
- 🧠 **PyTorch**: Framework học máy phục vụ nhận diện và xử lý mô hình AI.
- 🎯 **MTCNN (Multi-task Cascaded Convolutional Networks)**: Phát hiện và căn chỉnh vị trí khuôn mặt chính xác từ luồng camera.
- ⚡ **InceptionResNetV1 (FaceNet)**: Trích xuất véctơ đặc trưng khuôn mặt **512 chiều (512-dimensional embedding)**.
- 🔍 **FAISS (Facebook AI Similarity Search)**: Bộ tìm kiếm véctơ siêu tốc đệm trên RAM, giúp đối soát danh tính sinh viên dưới **0.01 giây**.

### ⚡ Backend API
- 🐍 **FastAPI**: Python Web Framework hiệu năng cao.
- 🧰 **SQLModel**: ORM kết hợp Pydantic v2 và SQLAlchemy phục vụ tương tác PostgreSQL.
- 💾 **PostgreSQL**: Cơ sở dữ liệu quan hệ lưu trữ thông tin người dùng, học phần, phiên điểm danh và nhật ký.
- 🔐 **Bảo mật & Mã hóa**: 
  - Mã hóa mật khẩu chuẩn **Argon2** & **Bcrypt** qua `pwdlib`.
  - Xác thực phiên làm việc chuẩn **JWT (JSON Web Token)** với phân quyền 3 vai trò (Admin, Lecturers, Students).
- 🧪 **Pytest**: Bộ kiểm thử tự động toàn bộ luồng tích hợp hệ thống.

### ☁️ Cloud Storage & Auto-Cleanup
- 🌩️ **Cloudinary**: Dịch vụ lưu trữ đám mây CDN tốc độ cao cho ảnh đại diện khuôn mặt sinh viên.
- 🧹 **Tự động Dọn dẹp (Auto-Cleanup Service)**: Dịch vụ ngầm tự động quét và xóa các ảnh bằng chứng điểm danh cũ quá **48 giờ (2 ngày)** để tối ưu dung lượng lưu trữ.

### 🎨 Frontend Modern Stack
- 🚀 **Next.js 16 (React 19)**: Framework React hiện đại nhất với App Router.
- 💃 **TypeScript**: Mã nguồn gõ kiểu chặt chẽ, an toàn.
- 🎨 **Tailwind CSS v4 & shadcn/ui**: Bộ linh kiện giao diện cao cấp (hơn 50 components) hỗ trợ Responsive & Dark/Light mode.
- 🛠️ **Hand-crafted Modular Services**: Lớp dịch vụ tương tác API phân chế rõ ràng (`admin.service.ts`, `lecturer.service.ts`, `student.service.ts`, `auth.service.ts`).

---

## 💎 Tính năng Cốt lõi (Core Features)

### 🛡️ 1. Quản trị viên (Admin Portal)
- **Bảng điều khiển Báo cáo (Dashboard)**: Thống kê tổng quan số lượng sinh viên, giảng viên, lớp học phần và tỷ lệ chuyên cần trung bình.
- **Nhật ký Hệ thống (System Audit Logs)**: Theo dõi real-time mọi hoạt động đăng nhập, duyệt khuôn mặt, khởi tạo phiên.
- **Quản lý Tài khoản & Lớp học phần**: Thêm mới, kích hoạt/khóa tài khoản, phân công giảng viên dạy từng môn.
- **Duyệt Khuôn mặt (Face Verification Approval)**: Kiểm duyệt ảnh mẫu đăng ký của sinh viên trước khi đưa vào bộ nhớ AI FAISS.

### 👨‍🏫 2. Giảng viên (Lecturer Portal)
- **Hồ sơ cá nhân & Lịch dạy**: Quản lý thông tin cá nhân và xem danh sách các lớp học phần phụ trách.
- **Quản lý Phiên điểm danh Live**: Khởi tạo phiên điểm danh thời gian thực, tùy chỉnh số phút muộn tối đa và ngưỡng nhận diện AI.
- **Bảng Chuyên cần & Chỉnh sửa**: Xem danh sách điểm danh, cập nhật trạng thái thủ công cho sinh viên khi cần.
- **Duyệt Đơn Khiếu nại (Appeals Handling)**: Tiếp nhận và phê duyệt các đơn phúc khảo chuyên cần của sinh viên kèm minh chứng nghỉ ốm/lý do cá nhân.

### 🎓 3. Sinh viên (Student Portal)
- **Trang chủ & Lịch học đã đăng ký**: Hiển thị đầy đủ các môn học phần đã đăng ký trong học kỳ kèm thông tin giảng viên và phòng học.
- **Điểm danh AI Trực tuyến (Live AI Check-in)**: Mở camera kiểm tra vị trí và nhận diện khuôn mặt tự động trong vài giây.
- **Lịch sử Điểm danh & Thống kê**: Xem tỷ lệ chuyên cần cá nhân và nhận cảnh báo khi vắng quá 20% số buổi.
- **Gửi Đơn Khiếu nại**: Gửi đơn giải trình chuyên cần kèm minh chứng tới giảng viên trực tiếp trên giao diện.

---

## 🛠️ Hướng dẫn Khởi chạy Hệ thống (Quick Start)

### 1. Khởi chạy Backend FastAPI
```bash
# Kích hoạt môi trường ảo Python
venv\Scripts\activate

# Khởi chạy máy chủ FastAPI Backend (Cổng mặc định 5050 hoặc 8000)
fastapi dev
```
👉 Tài liệu API tương tác Swagger UI: `http://localhost:5050/docs` hoặc `http://localhost:8000/docs`

### 2. Khởi chạy Frontend Next.js
```bash
# Chuyển vào thư mục frontend
cd frontend

# Chạy máy chủ phát triển Next.js
npm run dev
```
👉 Mở trình duyệt truy cập giao diện: `http://localhost:3000` hoặc `http://localhost:5173`

---

## 🔑 Tài khoản Thử nghiệm (Demo Accounts)

| Vai trò (Role) | Tên đăng nhập (Username) | Mật khẩu (Password) | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` | `admin123456` | Toàn quyền quản trị hệ thống |
| **Giảng viên (Lecturer)** | `2101` | `12345` | TS. Nguyễn Văn An |
| **Sinh viên (Student)** | `21080001` | `12345` | Nguyễn Đức Nghiêm |

---

## 📜 Giấy phép (License)
Dự án được phát triển và phân phối dưới giấy phép [MIT License](LICENSE).
