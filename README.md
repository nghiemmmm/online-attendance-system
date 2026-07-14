# Hệ thống Điểm danh Sinh viên Tự động bằng Nhận diện Khuôn mặt

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3A%22Test+Docker+Compose%22" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test%20Docker%20Compose/badge.svg" alt="Test Docker Compose"></a>
<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3A%22Test+Backend%22" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test%20Backend/badge.svg" alt="Test Backend"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="Coverage"></a>

**Hệ thống Điểm danh Sinh viên Tự động bằng Nhận diện Khuôn mặt (Online Attendance System with AI Face Recognition)** là một giải pháp chuyển đổi số toàn diện trong quản lý giáo dục. Hệ thống tự động hóa hoàn toàn quy trình điểm danh truyền thống bằng cách tích hợp camera thời gian thực qua WebRTC và đối soát danh tính siêu tốc qua mô hình học sâu (FaceNet, MTCNN) kết hợp cơ sở dữ liệu vector FAISS dưới 0.01 giây. Dự án hỗ trợ đắc lực cho Giảng viên trong việc kiểm soát chuyên cần lớp học, giúp Sinh viên tự thực hiện check-in nhanh chóng, minh bạch, đồng thời cung cấp cho Quản trị viên bức tranh thống kê toàn cảnh và nhật ký hoạt động bảo mật.

## Công nghệ & Tính năng

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) cho API backend Python.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) cho tương tác cơ sở dữ liệu SQL trong Python (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), được FastAPI sử dụng để xác thực dữ liệu và quản lý cấu hình.
  - 💾 [PostgreSQL](https://www.postgresql.org) làm cơ sở dữ liệu SQL chính.
- 🤖 **Bộ lõi AI & Thị giác máy tính (Computer Vision)**:
  - 🧠 [PyTorch](https://pytorch.org) phục vụ chạy các mô hình học máy.
  - 🎯 **MTCNN** để phát hiện và căn chỉnh khuôn mặt thời gian thực.
  - ⚡ **InceptionResNetV1 (FaceNet)** để trích xuất vector đặc trưng khuôn mặt 512 chiều.
  - 🔍 **FAISS (Facebook AI Similarity Search)** phục vụ tìm kiếm vector khuôn mặt tốc độ cao trên bộ nhớ đệm RAM.
- ☁️ **Lưu trữ đám mây & Tự động dọn dẹp**:
  - 🌩️ [Cloudinary](https://cloudinary.com) để lưu trữ hình ảnh qua CDN đám mây.
  - 🧹 **Dịch vụ tự động dọn dẹp chạy ngầm** để tự động xóa hình ảnh minh chứng điểm danh cũ quá 48 giờ (2 ngày).
- 🚀 [React](https://react.dev) cho ứng dụng Frontend.
  - 💃 Sử dụng TypeScript, React hooks, Next.js 16 (React 19), và các công nghệ frontend hiện đại.
  - 🎨 [Tailwind CSS](https://tailwindcss.com) và [shadcn/ui](https://ui.shadcn.com) cho các linh kiện giao diện người dùng.
  - 🤖 [Hand-crafted Modular Services](https://github.com/anhp1202/online-attendance-system/tree/main/frontend/services) để tích hợp API phân quyền người dùng.
  - 🧪 [Pytest](https://pytest.org) cho kiểm thử tích hợp và kiểm thử Backend.
  - 🦇 Hỗ trợ chế độ giao diện tối (Dark mode).
- 🐋 [Docker Compose](https://www.docker.com) phục vụ môi trường phát triển và vận hành thực tế.
- 🔒 Băm mật khẩu bảo mật mặc định (Argon2 & Bcrypt qua thư viện `pwdlib`).
- 🔑 Xác thực người dùng qua JWT (JSON Web Token) với cơ chế phân quyền dựa trên vai trò.
- 📫 Khôi phục mật khẩu qua Email.
- 📬 [Mailcatcher](https://mailcatcher.me) để kiểm thử gửi email dưới local trong quá trình phát triển.
- ✅ Kiểm thử tự động với [Pytest](https://pytest.org).
- 🚢 Hướng dẫn triển khai dự án bằng Docker Compose.
- 🏭 Quy trình CI/CD dựa trên GitHub Actions.

## Giao diện Dự án

### Trang Đăng nhập & Đăng ký
| Đăng nhập | Đăng ký |
| :---: | :---: |
| ![Đăng nhập](img/login.jpg) | ![Đăng ký](img/register.jpg) |

### Dashboard theo Vai trò
*   **Quản trị viên / Cán bộ (Admin/Staff):**
    ![Dashboard Admin](img/dashboard-staff.jpg)
*   **Giảng viên (Lecturer):**
    ![Dashboard Giảng viên](img/dashboard-lecturer.jpg)
*   **Sinh viên (Student):**
    ![Dashboard Sinh viên](img/dashboard-student.jpg)

---

## Kiến trúc Hệ thống & Quy trình CI/CD

### Sơ đồ kiến trúc nhận diện khuôn mặt và WebRTC
![Kiến trúc Hệ thống](img/system-architecture.png)

### Sơ đồ quy trình CI/CD kiểm thử và deploy
![Quy trình CI/CD](img/CICD%20(2).png)

---

## API Overview

Hệ thống cung cấp tập hợp các Restful API hỗ trợ đầy đủ luồng nghiệp vụ xác thực, điểm danh WebRTC AI, khiếu nại và báo cáo. Dưới đây là các nhóm API cốt lõi:

### 1. Xác thực & Quản lý phiên (`/auth` & `/sessions`)
*   `POST /auth/tokens`: Đăng nhập chuẩn JSON (hỗ trợ Remember Me cấp Refresh Token).
*   `POST /auth/access-tokens`: Đăng nhập tương thích OAuth2 Password Flow.
*   `POST /auth/token-refreshes`: Cấp mới Access Token từ Refresh Token hợp lệ.
*   `DELETE /sessions/current`: Đăng xuất phiên hiện tại (thu hồi Refresh Token hiện tại).
*   `DELETE /sessions`: Đăng xuất tất cả các thiết bị.

### 2. Đăng ký & Tài khoản (`/users`)
*   `POST /users/send-otp`: Yêu cầu gửi mã OTP xác thực về email sinh viên.
*   `POST /users/registrations`: Đăng ký tài khoản sinh viên sau khi xác thực mã OTP thành công.
*   `POST /users/signup`: Đăng ký tài khoản và tự động tạo hồ sơ sinh viên đi kèm.
*   `GET /users/me/profile`: Đọc hồ sơ cá nhân và trạng thái dữ liệu khuôn mặt.

### 3. Điểm danh AI & Camera Live (`/webrtc` & `/attendance`)
*   `POST /webrtc/offers`: Thiết lập kết nối WebRTC truyền luồng video từ camera lên server AI.
*   `GET /class-sections/my-sections`: Lấy danh sách lớp học phần đã đăng ký (sinh viên) hoặc giảng dạy (giảng viên).
*   `POST /class-sessions/{id}/attendance`: Điểm danh thủ công hoặc ghi nhận điểm danh tự động.

### 4. Khiếu nại Chuyên cần (`/appeals`)
*   `POST /appeals`: Sinh viên tạo đơn khiếu nại (kèm lý do và minh chứng ảnh).
*   `PATCH /appeals/{id}`: Giảng viên duyệt đơn khiếu nại (chấp nhận/từ chối).

---

## Cấu hình dự án

### ⚙️ Cấu hình Biến Môi trường (.env Configuration)
Trước khi khởi chạy hệ thống ở môi trường Production hoặc Local, bạn cần thiết lập các biến môi trường trong file `.env` theo danh sách các tham số cốt lõi sau:
#### 1. Các biến bảo mật & CSDL bắt buộc:
- `SECRET_KEY`: Chuỗi khóa bí mật dùng để ký mã hóa mã thông báo JWT Authentication.
- `FIRST_SUPERUSER`: Email tài khoản Quản trị viên khởi tạo ban đầu (Mặc định: `admin@example.com`).
- `FIRST_SUPERUSER_PASSWORD`: Mật khẩu tài khoản Quản trị viên khởi tạo ban đầu.
- `POSTGRES_SERVER`: Địa chỉ máy chủ CSDL PostgreSQL (Mặc định: `localhost`).
- `POSTGRES_PORT`: Cổng kết nối PostgreSQL (Mặc định: `5433` hoặc `5432`).
- `POSTGRES_USER` & `POSTGRES_PASSWORD`: Tài khoản và mật khẩu truy cập PostgreSQL.
- `POSTGRES_DB`: Tên cơ sở dữ liệu (Mặc định: `attendance`).
#### 2. Cấu hình Dịch vụ Đám mây Cloudinary:
- `CLOUDINARY_CLOUD_NAME`: Tên Cloud Name trên tài khoản Cloudinary (`dtdkqzqvo`).
- `CLOUDINARY_API_KEY`: Mã API Key kết nối (`825222872657695`).
- `CLOUDINARY_API_SECRET`: Mã API Secret xác thực lưu trữ ảnh đám mây.
### 🔑 Tạo Mã Bảo mật Secret Key
Để tạo một chuỗi `SECRET_KEY` an toàn ngẫu nhiên cho mã hóa JWT, bạn có thể chạy lệnh Python sau trong terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Hướng dẫn Khởi chạy Nhanh (Development)

### 1. Khởi chạy Backend (FastAPI)
```bash
venv\Scripts\activate
uvicorn app.main:app --reload
```

### 2. Khởi chạy Frontend (Next.js)
```bash
cd frontend
npm run dev
```

## Tài khoản Thử nghiệm

| Vai trò | Tên đăng nhập | Mật khẩu | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123456` | Quản trị toàn bộ hệ thống |
| **Lecturer** | `gv2101` | `12345` | TS. Nguyễn Văn An |
| **Student** | `21080001` | `12345` | Nguyễn Đức Nghiêm |

## Hướng dẫn Phát triển nâng cao

Tài liệu hướng dẫn phát triển chung: [development.md](./development.md).

Tài liệu bao gồm cách sử dụng Docker Compose, cấu hình domain cục bộ, biến môi trường `.env`,...

## Hạn chế Hiện tại

1.  **Hiệu năng đồng thời ⭐⭐⭐⭐⭐**: Gặp độ trễ xử lý khi nhiều sinh viên thực hiện nhận diện khuôn mặt cùng lúc.
2.  **Độ chính xác phụ thuộc môi trường ⭐⭐⭐⭐⭐**: Ảnh hưởng bởi ánh sáng yếu, góc nghiêng lớn, chất lượng camera hoặc khi sinh viên đeo khẩu trang, kính.
3.  **Chưa hỗ trợ Liveness Detection ⭐⭐⭐⭐⭐**: Chưa tích hợp kiểm tra thực thể sống nên có nguy cơ bị gian lận bằng hình ảnh hoặc video.


## Giấy phép

Dự án này được xây dựng cho mục đích học tập và trình diễn công nghệ.