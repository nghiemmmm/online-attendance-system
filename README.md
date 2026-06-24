# Hệ thống Điểm danh Khuôn mặt Trực tuyến

Hệ thống điểm danh trực tuyến dựa trên công nghệ nhận diện khuôn mặt (Face Recognition) kết nối với thời gian thực qua WebRTC.

## Kiến trúc Hệ thống
Dự án được xây dựng trên nền tảng công nghệ hiện đại:
- **Backend:** FastAPI (Python) + SQLModel.
- **Database:** PostgreSQL (hoặc SQLite cho môi trường Dev). Chi tiết thiết kế xem tại [DATABASE.md](DATABASE.md).
- **Trí tuệ nhân tạo (AI):** FaceNet (InceptionResnetV1) + MTCNN (Phát hiện khuôn mặt) + FAISS (Cơ sở dữ liệu Vector siêu tốc).
- **Frontend:** Next.js (React) + Tailwind CSS + Shadcn UI.
- **Giao thức Thời gian thực:** WebRTC (aiortc) truyền tải video và phân tích ảnh tự động.

## Các tính năng nổi bật
1. **Điểm danh tự động qua Camera:** Giảng viên chỉ cần mở phiên điểm danh. Hệ thống sẽ kết nối WebRTC và AI tự động "chộp" khung hình, nhận diện và chốt Có Mặt/Đi Muộn cho sinh viên.
2. **Luật điểm danh chặt chẽ:** Điểm danh sau thời gian `số phút muộn tối đa` sẽ tự động bị chuyển sang Đi Muộn. Khi đóng phiên, hệ thống tự động đánh `Vắng` cho những bạn chưa điểm danh.
3. **Khiếu nại tự động:** Sinh viên có quyền gửi đơn khiếu nại trong vòng 48 giờ sau khi buổi học kết thúc.
4. **Báo cáo và Backup:** Hỗ trợ xuất file Excel chuyên nghiệp (dùng `pandas`, `openpyxl`). Hỗ trợ gọi lệnh PostgreSQL Dump để sao lưu hệ thống.

---

## Hướng dẫn cài đặt và chạy (Dành cho Developer)

### 1. Khởi động Backend (FastAPI)
Yêu cầu: Đã cài đặt Python 3.10+

```bash
# 1. Tạo môi trường ảo và kích hoạt
python -m venv .venv
.\.venv\Scripts\activate   # Trên Windows

# 2. Cài đặt thư viện
pip install -r requirements.txt
pip install pandas openpyxl

# 3. Chạy Server
uvicorn app.main:app --host 0.0.0.0 --port 5050 --reload
```
> **Lưu ý:** Lần chạy đầu tiên sẽ hơi lâu (khoảng 3-5 phút) do hệ thống cần tải bộ pre-trained model `vggface2` về máy tính. 
> Sau khi chạy thành công, truy cập Swagger UI: [http://localhost:5050/api/docs](http://localhost:5050/api/docs)

### 2. Khởi động Frontend (Next.js)
Yêu cầu: Đã cài đặt Node.js 18+

```bash
cd frontend
npm install
npm run dev
```
> Truy cập giao diện tại: [http://localhost:3000](http://localhost:3000)

## Ghi chú về Dữ liệu Mẫu
Hệ thống sử dụng tài khoản theo định dạng:
- Admin: `admin` / pass: `admin`
- Giảng viên: `gv001` / pass: `password`
- Sinh viên: `sv001` / pass: `password`

*(Lưu ý: Bạn cần tạo dữ liệu này trong CSDL hoặc sử dụng script khởi tạo nếu có).*