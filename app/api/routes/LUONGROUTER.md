LUONG DANG KY THUONG BANG USERNAME/PASSWORD/ROLE

POST /users/signup
        |
        v
Client gui JSON body:
{
  "ten_dang_nhap": "nguyenvana",
  "password": "123456",
  "vai_tro": "SINH_VIEN"
}
        |
        v
Backend nhan TaiKhoanRegister tu request
        |
        v
Kiem tra ten_dang_nhap da ton tai chua
        |
        v
Neu da ton tai:
        |
        v
Tra loi 400: The account with this username already exists
        |
        v
Neu chua ton tai:
        |
        v
Convert TaiKhoanRegister thanh TaiKhoanCreate
        |
        v
Hash password thanh mat_khau_hash
        |
        v
Tao ban ghi TaiKhoan moi trong bang taikhoan
        |
        v
trang_thai mac dinh True
        |
        v
Tra ve TaiKhoanPublic

Response thanh cong gom:
- ma_tai_khoan
- ten_dang_nhap
- vai_tro
- trang_thai
- lan_dang_nhap_cuoi
- ngay_tao

Sau khi dang ky thanh cong, client dang nhap bang:

POST /login/access-token
        |
        v
Gui form-data:
username=<ten_dang_nhap>
password=<password>
        |
        v
Neu dung username/password va account.trang_thai=True
        |
        v
Backend tra access_token
        |
        v
Client dung Authorization: Bearer <access_token>


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


luong dang ky : TaiKhoanRegister từ request
 -> convert thành TaiKhoanCreate
 -> hash password
 -> insert TaiKhoan vào DB
