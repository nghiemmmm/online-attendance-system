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


promt 1 
Hãy đóng vai Senior FastAPI Architect.

Kiểm tra toàn bộ dự án FastAPI và đánh giá xem API có tuân thủ RESTful Best Practices hay không.

Kiểm tra:

1. HTTP Methods
- GET
- POST
- PUT
- PATCH
- DELETE

2. Endpoint Naming
- Có dùng danh từ số nhiều không
- Có dùng động từ trong URL không
- Có endpoint REST sai chuẩn không

3. URL Structure
- Nested Resource
- Versioning
- Prefix

4. HTTP Status Code
- 200
- 201
- 204
- 400
- 401
- 403
- 404
- 409
- 422
- 500

5. response_model

6. OpenAPI

Xuất kết quả theo bảng:

File
Route
Vấn đề
Mức độ
Đề xuất sửa

Không sửa code.
Chỉ audit.

promt 
Đóng vai Senior FastAPI Reviewer.

Kiểm tra toàn bộ Router.

Đánh giá xem Router có:

✓ Chỉ xử lý HTTP
✓ Không có business logic
✓ Không truy cập database
✓ Không import Repository
✓ Gọi Service
✓ Có response_model
✓ Có status_code
✓ Có summary
✓ Có description
✓ Dùng async
✓ Dùng APIRouter
✓ Dùng prefix
✓ Dùng tags

Tìm tất cả Router vi phạm.

Xuất:

File

Function

Violation

Recommendation

Severity

Không sửa code.


promt 9 
Kiểm tra toàn bộ dự án FastAPI.

Đánh giá Dependency Injection.

Kiểm tra:

Có dùng Depends đúng không

Có chỗ nào tự tạo Session()

Có chỗ nào new Service()

Có Singleton không cần thiết

Có Dependency lồng nhau

Có Depends trong Router

Có Dependency Override cho test

Có chỗ nào nên chuyển sang Depends

Xuất toàn bộ.


promt 8 
Kiểm tra toàn bộ FastAPI project.

Tìm tất cả endpoint chưa sử dụng Annotated.

Kiểm tra:

Depends

Query

Path

Header

Cookie

Body

Form

File

Liệt kê:

File

Function

Old Syntax

Recommended Syntax

Có tương thích FastAPI mới không

Không sửa code.

Chỉ audit.


promt 9 
Kiểm tra toàn bộ FastAPI project.

Tìm tất cả endpoint chưa sử dụng Annotated.

Kiểm tra:

Depends

Query

Path

Header

Cookie

Body

Form

File

Liệt kê:

File

Function

Old Syntax

Recommended Syntax

Có tương thích FastAPI mới không

Không sửa code.

Chỉ audit.



promt 9 
Kiểm tra toàn bộ Pydantic Models.

Đánh giá:

BaseModel

Field()

Validation

field_validator

model_validator

Default Value

Examples

Description

Type Hint

ConfigDict

Response Model

Request Model

Tìm model chưa chuẩn.

Không sửa code.


Kiểm tra kiến trúc:

Router

↓

Service

↓

Repository

↓

Database

Tìm mọi nơi vi phạm.

Ví dụ:

Router gọi Repository

Router truy cập DB

Service gọi Router

Repository gọi Router

Model gọi Service

Xuất toàn bộ Dependency Graph.


promt 6 
Kiểm tra Async.

Đánh giá:

Endpoint

Service

Repository

Database

HTTP Client

File IO

Tìm:

Blocking Code

Sync Function

time.sleep()

requests

open()

Subprocess

DB Sync Session

Xuất toàn bộ.


promt 5 
Kiểm tra Exception.

Đánh giá:

HTTPException

Custom Exception

Global Exception Handler

try except

raise

Business Exception

Validation Exception

Tìm nơi Service đang raise HTTPException.

Đề xuất chuyển sang Domain Exception.


Kiểm tra Exception.

Đánh giá:

HTTPException

Custom Exception

Global Exception Handler

try except

raise

Business Exception

Validation Exception

Tìm nơi Service đang raise HTTPException.

Đề xuất chuyển sang Domain Exception.

promt 5 
Kiểm tra Logging.

Tìm:

print()

logger

logging

exception

warning

debug

info

critical

Token

Password

JWT

Secret

PII

Liệt kê toàn bộ print cần thay.

Không sửa code.


promt5 
Kiểm tra cấu trúc dự án.

Đánh giá:

api/

routes/

services/

repositories/

schemas/

models/

core/

utils/

tests/

dependencies/

middlewares/

config/

So sánh với Best Practices FastAPI.

Cho điểm từng module.


Kiểm tra SOLID.

Single Responsibility

Open Closed

Liskov

Interface Segregation

Dependency Inversion

Tìm class vi phạm.

Tìm function quá dài.

Tìm class quá nhiều trách nhiệm.


promt 5 
Kiểm tra Clean Code.

Function Length

Class Length

Cyclomatic Complexity

Duplicate Code

Magic Number

Long Parameter

Long Method

Dead Code

Unused Import

Unused Variable

Nested If

Return Early

Đánh giá từng file.


Kiểm tra toàn bộ PEP8.

Line Length

Import Order

Naming

Whitespace

Blank Line

Trailing Space

Comment

Docstring

Type Hint

Constant

Class

Function

Variable

Module

Xuất toàn bộ lỗi.


Kiểm tra bảo mật.

JWT

OAuth2

Password Hash

SQL Injection

XSS

CORS

CSRF

Secret

Environment Variable

Rate Limit

Permission

Role

Authentication

Authorization

Tìm toàn bộ vấn đề.

promt 3 
Đóng vai Principal Python Architect.

Hãy audit toàn bộ dự án FastAPI như một Production Code Review.

Đánh giá theo các tiêu chí:

1. REST API Design
2. Router Best Practices
3. Service Layer
4. Repository Pattern
5. Dependency Injection
6. Annotated
7. Async/Await
8. SQLAlchemy
9. Pydantic v2
10. Exception Handling
11. Logging
12. Security
13. Testing
14. Performance
15. Clean Code
16. SOLID
17. PEP8
18. Project Structure
19. Documentation
20. OpenAPI

Đối với mỗi mục hãy:

- Cho điểm (/10)
- Liệt kê các file vi phạm
- Mô tả nguyên nhân
- Đề xuất cách sửa
- Ưu tiên (Critical / High / Medium / Low)

Cuối cùng:

- Tính điểm toàn bộ dự án.
- Liệt kê Top 20 việc nên sửa trước.
- Đề xuất lộ trình refactor theo từng giai đoạn.
- Không tự động sửa mã, chỉ audit và phân tích.