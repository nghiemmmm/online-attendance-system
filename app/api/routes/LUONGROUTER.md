POST /login/access-token
        ↓
Nhận username/password form-data
        ↓
Tìm TaiKhoan theo ten_dang_nhap
        ↓
Verify password với mat_khau_hash
        ↓
Kiểm tra trang_thai
        ↓
Cập nhật lan_dang_nhap_cuoi
        ↓
Tạo JWT {sub: ma_tai_khoan, role: vai_tro}
        ↓
Trả access_token
        ↓
Client dùng Authorization: Bearer token
        ↓
deps.py decode token
        ↓
Lấy current TaiKhoan
        ↓
API xử lý theo vai_tro

đăng nhập theo chuẩn OAuth2 Password Flow.  

JWT gồm 3 phần:

HEADER.PAYLOAD.SIGNATURE
Vì sao cần SIGNATURE?

Để chống sửa token.
Frontend sẽ lấy:
Frontend lưu token
access_token
rồi gửi kèm trong header mỗi lần gọi API cần đăng nhập
Frontend phải gửi:Authorization: Bearer abc.xyz.123
lay FastAPI lấy token từ heade -> def get_current_account(session: SessionDep, token: TokenDep) -> TaiKhoan: -> Nó decode JWT: -> Nó decode JWT: -> account = session.get(TaiKhoan, account_id) -> Nếu tài khoản tồn tại và trang_thai=True, trả về current_account
Nếu API yêu cầu admin: -> dependencies=[Depends(get_current_active_superuser)]