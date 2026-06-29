# Online Attendance System with AI Face Recognition

<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3A%22Test+Docker+Compose%22" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test%20Docker%20Compose/badge.svg" alt="Test Docker Compose"></a>
<a href="https://github.com/fastapi/full-stack-fastapi-template/actions?query=workflow%3A%22Test+Backend%22" target="_blank"><img src="https://github.com/fastapi/full-stack-fastapi-template/workflows/Test%20Backend/badge.svg" alt="Test Backend"></a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/full-stack-fastapi-template" target="_blank"><img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/full-stack-fastapi-template.svg" alt="Coverage"></a>

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
  - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🤖 **AI Core & Computer Vision**:
  - 🧠 [PyTorch](https://pytorch.org) for machine learning models.
  - 🎯 **MTCNN** for real-time face detection & alignment.
  - ⚡ **InceptionResNetV1 (FaceNet)** for 512-dimensional face embedding extraction.
  - 🔍 **FAISS (Facebook AI Similarity Search)** for high-speed RAM-cached vector search.
- ☁️ **Cloud Storage & Auto-Cleanup**:
  - 🌩️ [Cloudinary](https://cloudinary.com) for CDN image storage.
  - 🧹 **Background Auto-Cleanup Service** to purge attendance evidence images older than 48 hours (2 days).
- 🚀 [React](https://react.dev) for the frontend.
  - 💃 Using TypeScript, hooks, [Next.js 16 (React 19)](https://nextjs.org), and other parts of a modern frontend stack.
  - 🎨 [Tailwind CSS](https://tailwindcss.com) and [shadcn/ui](https://ui.shadcn.com) for the frontend components.
  - 🤖 [Hand-crafted Modular Services](https://github.com/anhp1202/online-attendance-system/tree/main/frontend/services) for role-based API integration.
  - 🧪 [Pytest](https://pytest.org) for Backend & Integration testing.
  - 🦇 Dark mode support.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default (Argon2 & Bcrypt via `pwdlib`).
- 🔑 JWT (JSON Web Token) authentication with role-based access control.
- 📫 Email based password recovery.
- 📬 [Mailcatcher](https://mailcatcher.me) for local email testing during development.
- ✅ Tests with [Pytest](https://pytest.org).
- 🚢 Deployment instructions using Docker Compose.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

### Dashboard Login

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Lecturer

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Interactive API Documentation

[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Configure

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

## Quick Start Development

### 1. Run Backend (FastAPI)
```bash
venv\Scripts\activate
fastapi dev
```

### 2. Run Frontend (Next.js)
```bash
cd frontend
npm run dev
```

## Demo Accounts

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123456` | Full system administration |
| **Lecturer** | `2101` | `12345` | TS. Nguyễn Văn An |
| **Student** | `21080001` | `12345` | Nguyễn Đức Nghiêm |

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.
