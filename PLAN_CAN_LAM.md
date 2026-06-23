# Plan cần làm cho dự án hệ thống điểm danh khuôn mặt

Ngày lập: 2026-06-21

Nguồn rà soát:

- Tài liệu yêu cầu: `XÁC ĐỊNH YÊU CẦU HỆ THỐNG(đã sửa).docx`
- Backend FastAPI trong `app/`
- Frontend Next.js trong `frontend/`
- Frontend Streamlit cũ trong `app/frontend/`
- Test suite trong `tests/`

Ghi chú kiểm tra:

- Đã trích xuất được nội dung DOCX bằng OOXML, tài liệu có khoảng 1196 đoạn nội dung.
- Chưa render được DOCX ra ảnh để kiểm tra bố cục vì runtime không tìm thấy LibreOffice/`soffice`.
- Backend test chưa chạy được: `python` không có trên PATH, `.venv` hiện bị hỏng vì trỏ tới Python cũ không còn tồn tại.
- Frontend lint đã chạy bằng `npm.cmd run lint` và đang fail: 36 errors, 30 warnings.

## 1. Tóm tắt tình trạng hiện tại

Dự án đã có nền backend, một phần model cơ sở dữ liệu, authentication, refresh token, Google OAuth, CRUD sinh viên/cán bộ, vài API thống kê lịch học/lịch dạy/khiếu nại và giao diện Next.js khá nhiều màn hình.

Tuy nhiên, so với tài liệu yêu cầu, dự án vẫn đang ở trạng thái prototype. Phần lõi quan trọng nhất là mở phiên điểm danh, nhận diện khuôn mặt qua webcam, ghi nhận điểm danh tự động, chống điểm danh hộ, lịch sử điểm danh cá nhân, xuất báo cáo, thông báo realtime, backup/restore và audit log vẫn chưa hoàn chỉnh hoặc chưa nối thành luồng chạy thật.

## 2. Lỗi và rủi ro cần xử lý ngay

### P0 - Làm dự án chạy và test được

- [ ] Tạo lại `.venv` vì `.venv/pyvenv.cfg` đang trỏ tới Python cũ: `C:\Users\Thai Tue\AppData\Local\Programs\Python\Python311\python.exe`.
- [ ] Bổ sung dependency còn thiếu trong `requirements.txt`: `sqlmodel`, `sqlalchemy`, `alembic`, `psycopg` hoặc `psycopg[binary]`, `pgvector`, `PyJWT`, `email-validator`. Kiểm tra thêm dependency cho test và migration.
- [ ] Chuẩn hóa package JWT: code đang `import jwt`, nhưng `requirements.txt` có `python-jose`; cần dùng thống nhất `PyJWT` hoặc đổi code sang `jose`.
- [ ] Sửa test suite cũ trong `tests/conftest.py` và `tests/api/routes/test_users.py` vì vẫn import `User`, `UserCreate`, `Item`, `hashed_password`, trong khi model hiện tại là `TaiKhoan`, `mat_khau_hash`.
- [ ] Chạy lại `pytest` sau khi sửa môi trường và test cũ.
- [ ] Sửa frontend lint trước khi build: hiện `npm.cmd run lint` fail 36 errors.
- [ ] Sửa `frontend/lib/api-client.ts`: khi gửi `FormData`, client vẫn gắn `Content-Type: application/json`, làm endpoint `/login/access-token` dễ bị lỗi.
- [ ] Sửa trang `frontend/app/page.tsx`: login hiện chỉ điều hướng demo theo role, chưa gọi `AuthService.login`.

### P0 - Bảo mật và cấu hình

- [ ] Không in test token khi khởi động trong `app/main.py`.
- [ ] Xoay lại secret/database credential nếu `.env` đã từng commit hoặc chia sẻ. Không lưu production `DATABASE_URL`, `SECRET_KEY`, Google client secret trực tiếp trong repo.
- [ ] Tạo `.env.example` sạch, chỉ chứa key mẫu không có secret thật.
- [ ] Kiểm tra `.gitignore` để chắc chắn `.env`, key, model checkpoint, file ảnh nhạy cảm không bị commit.
- [ ] CORS trong `app/main.py` đang hard-code localhost và không dùng hết `settings.all_cors_origins`; cần dùng cấu hình từ `.env`.

### P0 - Phân quyền đang lệch

- [ ] Chuẩn hóa hằng số vai trò. Tài liệu dùng `ADMIN`, `GIANG_VIEN`, `SINH_VIEN`; model mặc định `SINH_VIEN`; `init.sql` dùng `GIANG_VIEN`, `SINH_VIEN`; nhưng `deps.py` lại kiểm tra `SINHVIEN`, `CANBO`.
- [ ] Sửa các dependency role trong `app/api/deps.py`.
- [ ] Nhiều endpoint dành cho sinh viên/giảng viên hiện bị khóa bằng `get_current_active_superuser`, ví dụ lịch học, cảnh báo vắng, lịch dạy, khiếu nại. Cần đổi thành quyền đúng người dùng và kiểm tra ownership.

## 3. Đối chiếu yêu cầu trong DOCX với code hiện tại

### Sinh viên

- [ ] Thực hiện điểm danh bằng webcam: chưa có API/flow hoàn chỉnh để webcam -> nhận diện -> ghi `DiemDanh`.
- [ ] Tra cứu lịch sử điểm danh cá nhân: chưa có endpoint sinh viên tự xem lịch sử theo môn, học kỳ, trạng thái.
- [~] Kiểm tra điểm chuyên cần và cảnh báo: có service cảnh báo vắng, nhưng đang expose qua endpoint admin-only và chưa gắn vào màn hình sinh viên thật.
- [ ] Gửi khiếu nại điểm danh: model có `KhieuNai`, nhưng chưa có endpoint sinh viên tự tạo khiếu nại đúng quy định 48 giờ và mỗi buổi chỉ 1 lần.
- [~] Quản lý tài khoản cá nhân: có `/users/me`, đổi mật khẩu, login/logout; nhưng login theo tài liệu là email, code đang dùng `ten_dang_nhap`, chưa có khóa tài khoản sau 5 lần sai.
- [ ] Sinh viên chỉ được xem dữ liệu của chính mình: cần bổ sung kiểm tra ownership ở mọi endpoint sinh viên.

### Giảng viên

- [ ] Tạo và quản lý buổi học: có model `BuoiHoc`, nhưng chưa có router CRUD/mở phiên/đóng phiên.
- [ ] Mở/đóng phiên điểm danh: chưa có endpoint trạng thái phiên và chưa nối với WebRTC.
- [ ] Theo dõi sĩ số realtime: frontend có màn hình mock, backend chưa push realtime và chưa có tổng hợp live từ `DiemDanh`.
- [ ] Điều chỉnh tiêu chuẩn điểm danh: model `BuoiHoc` có `nguong_nhan_dien`, `so_phut_muon_toi_da`, nhưng chưa có API giảng viên quản lý theo lớp mình.
- [ ] Cập nhật điểm danh thủ công: chưa có endpoint giảng viên sửa trạng thái kèm `ly_do_chinh_sua` và audit log.
- [ ] Quản lý danh sách sinh viên trong lớp: có model `DangKyHocPhan`, nhưng chưa có router quản lý danh sách lớp.
- [~] Thống kê chuyên cần lớp học: có vài summary theo tháng/học kỳ, nhưng chưa đủ theo buổi, tháng, toàn khóa và chưa phân quyền giảng viên.
- [ ] Xuất báo cáo Excel/PDF: chưa thấy endpoint export.
- [~] Duyệt khiếu nại: có approve/reject trong `khieunai.py`, nhưng route đang admin-only và frontend gọi sai endpoint.

### Quản trị viên

- [~] Quản lý tài khoản/sinh viên/cán bộ: đã có một phần trong `/users`, `/sinh-vien`, `/canbo`.
- [ ] Quản lý ngành, học phần, lớp học phần, thời khóa biểu, đăng ký học phần: có model, nhưng thiếu router CRUD chính thức.
- [ ] Đăng ký/cập nhật ảnh khuôn mặt sinh viên: có model `AnhKhuonMat` và một số script AI, nhưng chưa có upload API, duyệt chất lượng ảnh, lưu ảnh chuẩn, tạo embedding và cập nhật index.
- [ ] Phân quyền sử dụng hệ thống: mới kiểm tra role đơn giản, chưa có ma trận quyền theo chức năng và ownership.
- [ ] Thống kê điểm danh toàn trường: frontend có màn hình mock, backend chưa đủ API theo lớp/khoa/học kỳ/sinh viên vắng quá 20%.
- [ ] Xuất dữ liệu điểm danh toàn trường: chưa có export CSV/Excel.
- [ ] Sao lưu và phục hồi dữ liệu: chưa có job backup 02:00, lưu 30 bản, restore qua giao diện, email cảnh báo khi fail.
- [ ] Xem lịch sử thao tác hệ thống: có middleware logging request, nhưng chưa có bảng audit log nghiệp vụ và màn hình đang dùng dữ liệu mock.

### Yêu cầu hệ thống

- [~] Đăng nhập/đăng xuất/đổi mật khẩu: có nền, nhưng cần sửa login frontend, role, token, lockout và last login.
- [ ] Sai mật khẩu quá 5 lần khóa 15 phút: chưa có model/cột đếm số lần sai, thời điểm khóa, logic mở khóa.
- [ ] Nhận diện khuôn mặt tự động: chưa nối pipeline nhận diện vào API điểm danh.
- [ ] Chống điểm danh hộ/liveness: chưa có kiểm tra chớp mắt/xoay đầu, chưa lưu sự cố chống giả mạo.
- [ ] Thông báo realtime: chưa có WebSocket/SSE/event bus cho giảng viên và sinh viên.
- [ ] Backup/restore: chưa có.
- [ ] Export báo cáo: chưa có.
- [ ] Audit log nghiệp vụ: chưa có bảng/log viewer thật.

## 4. Lỗi frontend cần sửa

- [ ] `frontend/app/page.tsx` đang login demo, không gọi backend.
- [ ] `frontend/services/student.service.ts` gọi endpoint không tồn tại hoặc sai tên: `/khieu-nai/`, `/khieunai/`, `/users/me/profile` PATCH.
- [ ] `frontend/services/lecturer.service.ts` gọi `/khieunai/`, `/khieunai/{id}/status`, `/lophocphan/`, trong khi backend hiện không có các endpoint này.
- [ ] `frontend/services/admin.service.ts` và `frontend/services/class.service.ts` gọi `/lophocphan/`, nhưng backend chưa có router lớp học phần.
- [ ] Nhiều màn hình vẫn dùng mock data: admin users, admin reports, admin audit, admin faces, student history, lecturer dashboard, lecturer live.
- [ ] Fix lint errors trong các file được báo bởi ESLint: `app/admin/classes/page.tsx`, `app/lecturer/claims/page.tsx`, `app/lecturer/classes/page.tsx`, `app/lecturer/reports/page.tsx`, `app/student/claims/page.tsx`, `app/student/profile/page.tsx`, `components/ui/carousel.tsx`, `components/ui/sidebar.tsx`, `components/ui/textarea.tsx`, `lib/api-client.ts`, các service.
- [ ] Chuẩn hóa encoding tiếng Việt trong source/frontend vì nhiều chuỗi hiển thị đang bị mojibake khi đọc qua terminal.

## 5. Lỗi backend/API cần sửa

- [ ] Thêm router CRUD còn thiếu: `nganh`, `hocphan`, `lophocphan`, `thoikhoabieu`, `buoihoc`, `dangkyhocphan`, `anhkhuonmat`, `anhdiemdanh`.
- [ ] Mở rộng `diemdanh.py`: tạo điểm danh tự động, cập nhật thủ công, lấy lịch sử theo sinh viên/lớp/buổi, chống ghi trùng, xử lý muộn/vắng.
- [ ] Mở rộng `khieunai.py`: sinh viên tạo khiếu nại, sinh viên xem khiếu nại của mình, giảng viên xem/duyệt theo lớp mình, kiểm tra 48 giờ và 1 khiếu nại/buổi.
- [ ] Sửa `/lich-hoc` và `/canbo/{id}/lich-day` để sinh viên/giảng viên tự truy cập theo tài khoản hiện tại thay vì truyền ID tùy ý.
- [ ] Thêm endpoint dashboard rõ ràng cho student, lecturer, admin thay vì frontend tự ghép mock.
- [ ] Login cần hỗ trợ email nếu tài liệu giữ yêu cầu “đăng nhập bằng email”.
- [ ] Cập nhật `lan_dang_nhap_cuoi` khi login thành công.
- [ ] Thêm lockout sau 5 lần sai mật khẩu trong 15 phút.
- [ ] Chuẩn hóa `app/core/security/__init__.py` và `app/core/security/security.py`; hiện có 2 implementation khác nhau.
- [ ] Xử lý refresh token tốt hơn ở frontend: lưu token khi remember me, refresh access token khi hết hạn, logout revoke token.

## 6. Database và migration cần bổ sung

- [ ] Thêm constraint/check enum cho `vai_tro`, `trang_thai` điểm danh, `phuong_thuc`, trạng thái khiếu nại, trạng thái buổi học.
- [ ] Thêm unique constraint để mỗi sinh viên chỉ gửi 1 khiếu nại cho 1 bản ghi/buổi điểm danh nếu giữ đúng quy định.
- [ ] Thêm field bằng chứng khiếu nại nếu tài liệu yêu cầu “bằng chứng đính kèm”.
- [ ] Thêm bảng hoặc field cho audit log nghiệp vụ: user, action, entity, entity_id, before/after, ip, user_agent, timestamp.
- [ ] Thêm bảng cấu hình hệ thống nếu cần quản lý ngưỡng nhận diện, số phút muộn, backup schedule.
- [ ] Thêm cột cho account lockout: failed_login_count, locked_until.
- [ ] Thêm dữ liệu chất lượng ảnh khuôn mặt: trạng thái duyệt, điểm chất lượng, lý do từ chối, thời điểm duyệt, người duyệt.
- [ ] Seed data trong `init.sql` đang dùng password giả như `hash_gv001`; cần dùng hash thật tương thích `passlib`.
- [ ] Kiểm tra migration cuối cùng với model hiện tại bằng `alembic upgrade head` trên database sạch.

## 7. Nhận diện khuôn mặt và WebRTC

- [ ] Chọn 1 pipeline nhận diện chính, tránh phân tán giữa `face_recognition.py`, `face_verification.py`, `facenet_loader.py`, `models.py`, `create_ebedding_faiss.py`.
- [ ] Xây API đăng ký ảnh khuôn mặt: upload, validate mặt duy nhất, chất lượng ảnh, tạo embedding, lưu DB và cập nhật FAISS/vector store.
- [ ] Xây API điểm danh tự động: nhận frame/ảnh, detect face, extract embedding, so khớp với sinh viên trong lớp, ghi `DiemDanh`.
- [ ] Nối `app/api/routes/ketnoi_router.py` với pipeline nhận diện; hiện WebRTC mới nhận offer và echo message, chưa ghi nhận điểm danh.
- [ ] Thêm liveness/anti-spoof: chớp mắt, xoay đầu nhẹ, kiểm tra ảnh/video replay ở mức phù hợp đồ án.
- [ ] Lưu ảnh bằng chứng điểm danh vào `AnhDiemDanh`.
- [ ] Benchmark độ chính xác, false accept, false reject theo yêu cầu: đúng trên 95%, nhận sai dưới 1%, từ chối người thật không quá 5%.
- [ ] Benchmark tốc độ: nhận diện mỗi sinh viên không quá 1 giây, hiển thị kết quả trong 3 giây.

## 8. Báo cáo, thông báo, backup, audit

- [ ] Export Excel/CSV theo buổi, lớp, môn, học kỳ, sinh viên.
- [ ] Quy tắc tên file export: `MaLop_Buoi_Ngay`.
- [ ] Thêm PDF export nếu giữ yêu cầu giảng viên xuất Excel hoặc PDF.
- [ ] Realtime notification cho giảng viên khi sinh viên điểm danh thành công hoặc nghi ngờ.
- [ ] Notification cho sinh viên khi có kết quả điểm danh hoặc kết quả xử lý khiếu nại.
- [ ] Job backup hằng ngày 02:00, giữ tối thiểu 30 bản.
- [ ] Giao diện admin phục hồi backup và cảnh báo email khi backup fail.
- [ ] Audit log lưu tối thiểu 1 năm cho login, sửa điểm danh, duyệt khuôn mặt, duyệt khiếu nại.

## 9. Tài liệu cần sửa

- [ ] `README.md` đang mô tả endpoint cũ như `/api/students`, `/api/teachers`, `/api/requests`, không khớp backend hiện tại.
- [ ] README nói backend chạy port 8000, trong `settings` mặc định là 5050.
- [ ] README nói lớp học trực tuyến/WebRTC, còn DOCX mô tả lớp học trực tiếp quy mô lớn. Cần thống nhất phạm vi.
- [ ] `frontend/README.md` vẫn là README mặc định Next.js, cần thay bằng hướng dẫn chạy frontend thật.
- [ ] Thêm tài liệu API hiện tại: auth, role, business flow, response schema.
- [ ] Thêm sơ đồ luồng nghiệp vụ: đăng ký khuôn mặt, mở phiên điểm danh, điểm danh tự động, sửa thủ công, khiếu nại, xuất báo cáo.

## 10. Lộ trình đề xuất

### Giai đoạn 1 - Ổn định nền chạy

- [ ] Recreate `.venv`, cài đủ backend dependencies.
- [ ] Sửa requirements/JWT/security.
- [ ] Sửa test suite cũ để import đúng model hiện tại.
- [ ] Sửa frontend login thật và api client.
- [ ] Fix frontend lint blocker.
- [ ] Chạy được: `pytest`, `npm.cmd run lint`, `npm.cmd run build`.

### Giai đoạn 2 - Chuẩn hóa auth và phân quyền

- [ ] Chốt role chuẩn: `ADMIN`, `GIANG_VIEN`, `SINH_VIEN`.
- [ ] Sửa toàn bộ seed, model, deps, frontend role mapping.
- [ ] Thêm ownership checks: sinh viên chỉ xem của mình, giảng viên chỉ xem lớp mình phụ trách.
- [ ] Thêm lockout login, last login, revoke token đúng flow.

### Giai đoạn 3 - Hoàn thiện nghiệp vụ dữ liệu

- [ ] Thêm CRUD route cho ngành, học phần, lớp học phần, lịch học, buổi học, đăng ký học phần.
- [ ] Thêm API quản lý thành viên lớp.
- [ ] Thêm API sinh viên xem lịch, lịch sử điểm danh, cảnh báo vắng.
- [ ] Thêm API giảng viên xem lịch dạy, lớp đang dạy, sĩ số, thống kê.

### Giai đoạn 4 - Hoàn thiện điểm danh lõi

- [ ] API mở/đóng phiên điểm danh.
- [ ] API điểm danh thủ công.
- [ ] API điểm danh tự động bằng ảnh/frame.
- [ ] Tính `CO_MAT`, `MUON`, `VANG` theo thời gian và cấu hình buổi học.
- [ ] Lưu ảnh bằng chứng và độ tin cậy.
- [ ] Chống ghi trùng theo `(ma_sinh_vien, ma_buoi_hoc)`.

### Giai đoạn 5 - Face recognition và realtime

- [ ] Đăng ký ảnh khuôn mặt và embedding.
- [ ] Nối WebRTC/live session với nhận diện thật.
- [ ] Liveness cơ bản.
- [ ] Notification realtime.
- [ ] Benchmark độ chính xác/tốc độ.

### Giai đoạn 6 - Khiếu nại, báo cáo, admin vận hành

- [ ] Sinh viên gửi khiếu nại đúng rule.
- [ ] Giảng viên duyệt/từ chối đúng ownership.
- [ ] Export CSV/Excel/PDF.
- [ ] Audit log.
- [ ] Backup/restore.
- [ ] Dashboard admin/giảng viên/sinh viên dùng API thật.

### Giai đoạn 7 - QA và hoàn thiện đồ án

- [ ] Unit test service/crud.
- [ ] API integration test theo role.
- [ ] Frontend e2e smoke test: login, xem lịch, mở phiên, điểm danh, khiếu nại, export.
- [ ] Test migration trên database sạch.
- [ ] Test hiệu năng lớp 70 sinh viên.
- [ ] Cập nhật README và tài liệu hướng dẫn demo.

## 11. Thứ tự làm ngay trong 1-2 ngày tới

- [ ] Sửa môi trường: recreate `.venv`, update `requirements.txt`, chạy import backend.
- [ ] Sửa test suite cũ để ít nhất collection không lỗi.
- [ ] Sửa role constants và `deps.py`.
- [ ] Sửa frontend login thật: `app/page.tsx`, `AuthService`, `api-client`.
- [ ] Thêm router tối thiểu cho `lophocphan`, `buoihoc`, `diemdanh`, `khieu-nai` theo luồng demo.
- [ ] Sửa endpoint frontend đang gọi sai tên.
- [ ] Chạy lại `pytest` và `npm.cmd run lint`.

