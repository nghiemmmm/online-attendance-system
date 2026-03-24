# Hệ thống Điểm danh bằng Khuôn mặt

Hệ thống tích hợp thuật toán nhận diện khuôn mặt với WebRTC để tự động điểm danh sinh viên trong lớp học trực tuyến.

## 🚀 Cách chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

Chỉnh sửa file `.env`:
```env
# FastAPI Backend
API_URL=http://localhost:8000
PORT=8000

# Streamlit Frontend
STREAMLIT_SERVER_PORT=8501
```

### 3. Chạy FastAPI Backend

```bash
uvicorn app.main:app --reload
```

Backend sẽ chạy tại: http://localhost:8000

### 4. Chạy Streamlit Frontend

```bash
streamlit run app/frontend/streamlit_ui.py
```

Frontend sẽ chạy tại: http://localhost:8501

## 📁 Cấu trúc dự án

```
app/
├── main.py                 # FastAPI entry point
├── core/
│   ├── config.py          # Cấu hình ứng dụng
│   └── security.py        # Xác thực & bảo mật
├── api/
│   └── routes/            # API endpoints
├── database/              # Database models & CRUD
├── services/              # Business logic
├── frontend/              # Streamlit UI
│   ├── streamlit_ui.py    # Main UI entry point
│   ├── pages/            # UI pages
│   ├── api_client.py     # API client for backend
│   └── settings.py       # Settings page
└── utils/                 # Utilities
```

## 🔌 API Endpoints

### Học sinh
- `GET /api/students` - Lấy danh sách học sinh
- `POST /api/students` - Thêm học sinh mới
- `PUT /api/students/{id}` - Cập nhật học sinh
- `DELETE /api/students/{id}` - Xóa học sinh

### Giáo viên
- `GET /api/teachers` - Lấy danh sách giáo viên
- `POST /api/teachers` - Thêm giáo viên mới
- `PUT /api/teachers/{id}` - Cập nhật giáo viên
- `DELETE /api/teachers/{id}` - Xóa giáo viên

### Điểm danh
- `GET /api/attendance` - Lấy lịch sử điểm danh
- `POST /api/attendance` - Ghi nhận điểm danh
- `GET /api/attendance/stats` - Thống kê điểm danh

### Yêu cầu
- `GET /api/requests` - Lấy danh sách yêu cầu
- `POST /api/requests` - Tạo yêu cầu mới
- `PUT /api/requests/{id}` - Cập nhật trạng thái
- `GET /api/requests/stats` - Thống kê yêu cầu

## 👥 Vai trò người dùng

### Admin
- Quản lý học sinh và giáo viên
- Xem dashboard thống kê
- Quản lý hệ thống

### Requester (Người yêu cầu)
- Ghi nhận điểm danh
- Tạo báo cáo

### Responder (Người phản hồi)
- Xử lý yêu cầu
- Xem thống kê yêu cầu

## 🛠️ Công nghệ sử dụng

- **Backend**: FastAPI, Python
- **Frontend**: Streamlit
- **Database**: SQLAlchemy (có thể cấu hình)
- **AI/ML**: Face recognition models
- **Real-time**: WebRTC integration

## 📝 Lưu ý

- Đảm bảo FastAPI backend chạy trước khi khởi động Streamlit
- Kiểm tra API_URL trong file `.env` đúng với port của FastAPI
- Cần cài đặt các dependencies cho face recognition nếu sử dụng

## 🔧 Troubleshooting

### Lỗi kết nối API
- Kiểm tra FastAPI có chạy tại đúng port không
- Kiểm tra API_URL trong `.env`
- Xem logs của FastAPI để debug

### Lỗi Streamlit
- Đảm bảo tất cả dependencies đã cài đặt
- Kiểm tra file paths trong code
- Xem logs của Streamlit

## 📞 Hỗ trợ

Liên hệ: support@facerecognition.edu.vn