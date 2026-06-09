CREATE EXTENSION IF NOT EXISTS vector;

/* =========================================================
   RESET DATABASE
========================================================= */

TRUNCATE TABLE
anhdiemdanh,
anhkhuonmat,
dangkyhocphan,
khieunai,
diemdanh,
buoihoc,
thoikhoabieu,
lophocphan,
hocphan,
sinhvien,
canbo,
oauth_identity,
taikhoan,
nganh
RESTART IDENTITY CASCADE;


/* =========================================================
   NGÀNH
========================================================= */

INSERT INTO nganh (
    ten_nganh,
    mo_ta
)
VALUES (
    'Công nghệ thông tin',
    'Ngành CNTT'
);


/* =========================================================
   TÀI KHOẢN
========================================================= */

INSERT INTO taikhoan (
    ten_dang_nhap,
    mat_khau_hash,
    vai_tro,
    trang_thai,
    ngay_tao
)
VALUES
(
    'gv001',
    'hash_gv001',
    'GIANG_VIEN',
    true,
    NOW()
),
(
    'sv001',
    'hash_sv001',
    'SINH_VIEN',
    true,
    NOW()
);


/* =========================================================
   KIỂM TRA
========================================================= */

SELECT * FROM taikhoan;


/* =========================================================
   CÁN BỘ
========================================================= */

INSERT INTO canbo (
    ho,
    ten,
    dien_thoai,
    gioi_tinh,
    ngay_sinh,
    google_email,
    ma_tai_khoan,
    chuc_vu,
    trang_thai
)
VALUES (
    'Nguyễn',
    'Văn A',
    '0909000001',
    'Nam',
    '1985-05-20',
    'gva@university.edu.vn',
    (SELECT ma_tai_khoan
     FROM taikhoan
     WHERE ten_dang_nhap = 'gv001'),
    'Giảng viên',
    true
);


/* =========================================================
   KIỂM TRA
========================================================= */

SELECT * FROM canbo;


/* =========================================================
   SINH VIÊN
========================================================= */

INSERT INTO sinhvien (
    ho,
    ten,
    ngay_sinh,
    gioi_tinh,
    dien_thoai,
    google_email,
    ma_nganh,
    ma_tai_khoan,
    trang_thai_hoc,
    thoi_gian_bat_dau_hoc
)
VALUES (
    'Trần',
    'Văn B',
    '2004-03-12',
    'Nam',
    '0911111111',
    'sv001@student.edu.vn',
    (SELECT ma_nganh FROM nganh LIMIT 1),
    (
        SELECT ma_tai_khoan
        FROM taikhoan
        WHERE ten_dang_nhap = 'sv001'
    ),
    true,
    NOW()
);


/* =========================================================
   KIỂM TRA
========================================================= */

SELECT * FROM sinhvien;


/* =========================================================
   HỌC PHẦN
========================================================= */

INSERT INTO hocphan (
    ma_hoc_phan,
    ten_hoc_phan,
    mo_ta,
    so_tin_chi,
    trang_thai
)
VALUES (
    101,
    'Cơ sở dữ liệu',
    'Môn học SQL',
    3,
    true
);


/* =========================================================
   KIỂM TRA
========================================================= */

SELECT * FROM hocphan;


/* =========================================================
   LỚP HỌC PHẦN
========================================================= */

INSERT INTO lophocphan (
    ma_hoc_phan,
    ma_can_bo,
    hoc_ky,
    nam_hoc,
    ty_le_chuyen_can_toi_thieu,
    trang_thai,
    ngay_tao
)
VALUES (
    101,
    (SELECT ma_can_bo FROM canbo LIMIT 1),
    1,
    '2025-2026',
    0.8,
    true,
    NOW()
);


/* =========================================================
   KIỂM TRA
========================================================= */

SELECT * FROM lophocphan;


/* =========================================================
   BUỔI HỌC
========================================================= */

INSERT INTO buoihoc (
    ma_lop_hoc_phan,
    ngay_hoc,
    gio_bat_dau,
    gio_ket_thuc,
    so_buoi,
    trang_thai,
    nguong_nhan_dien,
    so_phut_muon_toi_da,
    ghi_chu
)
VALUES (
    (SELECT ma_lop_hoc_phan FROM lophocphan LIMIT 1),
    '2025-09-08',
    '07:00',
    '09:30',
    1,
    'DA_KET_THUC',
    0.5,
    15,
    'Buổi học đầu tiên'
);


/* =========================================================
   KIỂM TRA
========================================================= */

SELECT * FROM buoihoc;


/* =========================================================
   ĐIỂM DANH
========================================================= */

INSERT INTO diemdanh (
    ma_sinh_vien,
    ma_buoi_hoc,
    trang_thai,
    phuong_thuc,
    do_tin_cay,
    thoi_diem_diem_danh
)
VALUES (
    (SELECT ma_sinh_vien FROM sinhvien LIMIT 1),
    (SELECT ma_buoi_hoc FROM buoihoc LIMIT 1),
    'CO_MAT',
    'KHUON_MAT',
    0.95,
    NOW()
);


/* =========================================================
   KIỂM TRA
========================================================= */

SELECT * FROM diemdanh;


/* =========================================================
   KHIẾU NẠI
========================================================= */

INSERT INTO khieunai (
    ma_diem_danh,
    ma_sinh_vien,
    ly_do,
    trang_thai,
    ngay_gui,
    ma_can_bo_xu_ly,
    ghi_chu_xu_ly,
    ngay_xu_ly
)
VALUES (
    (SELECT ma_diem_danh FROM diemdanh LIMIT 1),
    (SELECT ma_sinh_vien FROM sinhvien LIMIT 1),
    'Em vào lớp đúng giờ nhưng hệ thống nhận diện chậm',
    'DA_DUYET',
    NOW(),
    (SELECT ma_can_bo FROM canbo LIMIT 1),
    'Đã kiểm tra camera',
    NOW()
);


/* =========================================================
   KIỂM TRA CUỐI
========================================================= */

SELECT * FROM khieunai;
