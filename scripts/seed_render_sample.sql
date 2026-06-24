BEGIN;

-- Sample data for the Render PostgreSQL database.
-- This script is intentionally non-destructive: it does not TRUNCATE or DELETE.
-- Default password hash below is intended for the demo password: password

INSERT INTO nganh (ma_nganh, ten_nganh, mo_ta)
SELECT 101, 'Cong nghe thong tin', 'Dao tao phat trien phan mem, co so du lieu va he thong thong tin'
WHERE NOT EXISTS (SELECT 1 FROM nganh WHERE ma_nganh = 101);

INSERT INTO nganh (ma_nganh, ten_nganh, mo_ta)
SELECT 102, 'He thong thong tin', 'Dao tao phan tich nghiep vu, quan tri du lieu va ung dung doanh nghiep'
WHERE NOT EXISTS (SELECT 1 FROM nganh WHERE ma_nganh = 102);

INSERT INTO taikhoan (ma_tai_khoan, ten_dang_nhap, mat_khau_hash, vai_tro, trang_thai, ngay_tao)
SELECT 101, 'admin@university.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'ADMIN', true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM taikhoan WHERE ten_dang_nhap = 'admin@university.edu.vn');

INSERT INTO taikhoan (ma_tai_khoan, ten_dang_nhap, mat_khau_hash, vai_tro, trang_thai, ngay_tao)
SELECT 102, 'gv001@university.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'GIANG_VIEN', true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM taikhoan WHERE ten_dang_nhap = 'gv001@university.edu.vn');

INSERT INTO taikhoan (ma_tai_khoan, ten_dang_nhap, mat_khau_hash, vai_tro, trang_thai, ngay_tao)
SELECT 103, 'gv002@university.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'GIANG_VIEN', true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM taikhoan WHERE ten_dang_nhap = 'gv002@university.edu.vn');

INSERT INTO taikhoan (ma_tai_khoan, ten_dang_nhap, mat_khau_hash, vai_tro, trang_thai, ngay_tao)
SELECT 104, 'sv001@student.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'SINH_VIEN', true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM taikhoan WHERE ten_dang_nhap = 'sv001@student.edu.vn');

INSERT INTO taikhoan (ma_tai_khoan, ten_dang_nhap, mat_khau_hash, vai_tro, trang_thai, ngay_tao)
SELECT 105, 'sv002@student.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'SINH_VIEN', true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM taikhoan WHERE ten_dang_nhap = 'sv002@student.edu.vn');

INSERT INTO taikhoan (ma_tai_khoan, ten_dang_nhap, mat_khau_hash, vai_tro, trang_thai, ngay_tao)
SELECT 106, 'sv003@student.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'SINH_VIEN', true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM taikhoan WHERE ten_dang_nhap = 'sv003@student.edu.vn');

INSERT INTO canbo (ma_can_bo, ho, ten, dien_thoai, gioi_tinh, ngay_sinh, google_email, ma_tai_khoan, chuc_vu, trang_thai)
SELECT 101, 'Nguyen', 'Van An', '0901000001', 'Nam', '1984-05-20', 'gv001@university.edu.vn', 102, 'Giang vien', true
WHERE NOT EXISTS (SELECT 1 FROM canbo WHERE ma_can_bo = 101);

INSERT INTO canbo (ma_can_bo, ho, ten, dien_thoai, gioi_tinh, ngay_sinh, google_email, ma_tai_khoan, chuc_vu, trang_thai)
SELECT 102, 'Tran', 'Thi Binh', '0901000002', 'Nu', '1988-09-12', 'gv002@university.edu.vn', 103, 'Giang vien', true
WHERE NOT EXISTS (SELECT 1 FROM canbo WHERE ma_can_bo = 102);

INSERT INTO sinhvien (ma_sinh_vien, ho, ten, ngay_sinh, gioi_tinh, dien_thoai, google_email, ma_nganh, ma_tai_khoan, trang_thai_hoc, thoi_gian_bat_dau_hoc)
SELECT 101, 'Le', 'Minh Khang', '2004-03-12', 'Nam', '0911000001', 'sv001@student.edu.vn', 101, 104, true, '2023-09-01 08:00:00'
WHERE NOT EXISTS (SELECT 1 FROM sinhvien WHERE ma_sinh_vien = 101);

INSERT INTO sinhvien (ma_sinh_vien, ho, ten, ngay_sinh, gioi_tinh, dien_thoai, google_email, ma_nganh, ma_tai_khoan, trang_thai_hoc, thoi_gian_bat_dau_hoc)
SELECT 102, 'Pham', 'Thu Ha', '2004-07-22', 'Nu', '0911000002', 'sv002@student.edu.vn', 101, 105, true, '2023-09-01 08:00:00'
WHERE NOT EXISTS (SELECT 1 FROM sinhvien WHERE ma_sinh_vien = 102);

INSERT INTO sinhvien (ma_sinh_vien, ho, ten, ngay_sinh, gioi_tinh, dien_thoai, google_email, ma_nganh, ma_tai_khoan, trang_thai_hoc, thoi_gian_bat_dau_hoc)
SELECT 103, 'Do', 'Quoc Viet', '2003-11-05', 'Nam', '0911000003', 'sv003@student.edu.vn', 102, 106, true, '2022-09-01 08:00:00'
WHERE NOT EXISTS (SELECT 1 FROM sinhvien WHERE ma_sinh_vien = 103);

INSERT INTO hocphan (ma_hoc_phan, ten_hoc_phan, mo_ta, so_tin_chi, trang_thai)
SELECT 101, 'Co so du lieu', 'Thiet ke va truy van co so du lieu quan he', 3, true
WHERE NOT EXISTS (SELECT 1 FROM hocphan WHERE ma_hoc_phan = 101);

INSERT INTO hocphan (ma_hoc_phan, ten_hoc_phan, mo_ta, so_tin_chi, trang_thai)
SELECT 102, 'Lap trinh Web', 'Xay dung ung dung web full-stack', 3, true
WHERE NOT EXISTS (SELECT 1 FROM hocphan WHERE ma_hoc_phan = 102);

INSERT INTO hocphan (ma_hoc_phan, ten_hoc_phan, mo_ta, so_tin_chi, trang_thai)
SELECT 103, 'Tri tue nhan tao', 'Nhap mon hoc may va ung dung AI', 3, true
WHERE NOT EXISTS (SELECT 1 FROM hocphan WHERE ma_hoc_phan = 103);

INSERT INTO lophocphan (ma_lop_hoc_phan, ma_hoc_phan, ma_can_bo, hoc_ky, nam_hoc, ty_le_chuyen_can_toi_thieu, trang_thai, ngay_tao)
SELECT 101, 101, 101, 1, '2025-2026', 0.8, true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM lophocphan WHERE ma_lop_hoc_phan = 101);

INSERT INTO lophocphan (ma_lop_hoc_phan, ma_hoc_phan, ma_can_bo, hoc_ky, nam_hoc, ty_le_chuyen_can_toi_thieu, trang_thai, ngay_tao)
SELECT 102, 102, 101, 1, '2025-2026', 0.8, true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM lophocphan WHERE ma_lop_hoc_phan = 102);

INSERT INTO lophocphan (ma_lop_hoc_phan, ma_hoc_phan, ma_can_bo, hoc_ky, nam_hoc, ty_le_chuyen_can_toi_thieu, trang_thai, ngay_tao)
SELECT 103, 103, 102, 1, '2025-2026', 0.75, true, NOW()
WHERE NOT EXISTS (SELECT 1 FROM lophocphan WHERE ma_lop_hoc_phan = 103);

INSERT INTO dangkyhocphan (ma_sinh_vien, ma_lop_hoc_phan, trang_thai, ngay_dang_ky)
SELECT v.ma_sinh_vien, v.ma_lop_hoc_phan, true, NOW()
FROM (VALUES
    (101, 101), (102, 101), (103, 101),
    (101, 102), (102, 102),
    (102, 103), (103, 103)
) AS v(ma_sinh_vien, ma_lop_hoc_phan)
WHERE NOT EXISTS (
    SELECT 1 FROM dangkyhocphan d
    WHERE d.ma_sinh_vien = v.ma_sinh_vien
      AND d.ma_lop_hoc_phan = v.ma_lop_hoc_phan
);

INSERT INTO thoikhoabieu (ma_thoi_khoa_bieu, ma_lop_hoc_phan, thu, tiet_bat_dau, tiet_ket_thuc, gio_bat_dau, gio_ket_thuc, ngay_bat_dau, ngay_ket_thuc)
SELECT 101, 101, 2, 1, 3, '07:00', '09:30', '2025-09-01', '2025-12-31'
WHERE NOT EXISTS (SELECT 1 FROM thoikhoabieu WHERE ma_thoi_khoa_bieu = 101);

INSERT INTO thoikhoabieu (ma_thoi_khoa_bieu, ma_lop_hoc_phan, thu, tiet_bat_dau, tiet_ket_thuc, gio_bat_dau, gio_ket_thuc, ngay_bat_dau, ngay_ket_thuc)
SELECT 102, 102, 4, 4, 6, '09:45', '12:15', '2025-09-01', '2025-12-31'
WHERE NOT EXISTS (SELECT 1 FROM thoikhoabieu WHERE ma_thoi_khoa_bieu = 102);

INSERT INTO thoikhoabieu (ma_thoi_khoa_bieu, ma_lop_hoc_phan, thu, tiet_bat_dau, tiet_ket_thuc, gio_bat_dau, gio_ket_thuc, ngay_bat_dau, ngay_ket_thuc)
SELECT 103, 103, 6, 7, 9, '13:00', '15:30', '2025-09-01', '2025-12-31'
WHERE NOT EXISTS (SELECT 1 FROM thoikhoabieu WHERE ma_thoi_khoa_bieu = 103);

INSERT INTO buoihoc (ma_buoi_hoc, ma_lop_hoc_phan, ngay_hoc, gio_bat_dau, gio_ket_thuc, so_buoi, trang_thai, nguong_nhan_dien, so_phut_muon_toi_da, ghi_chu, thoi_gian_mo_diem_danh, thoi_gian_dong_diem_danh)
SELECT v.ma_buoi_hoc, v.ma_lop_hoc_phan, v.ngay_hoc::date, v.gio_bat_dau::time, v.gio_ket_thuc::time, v.so_buoi, v.trang_thai, 0.5, 15, v.ghi_chu, (v.ngay_hoc::date + v.gio_bat_dau::time), (v.ngay_hoc::date + v.gio_ket_thuc::time)
FROM (VALUES
    (101, 101, '2025-09-08', '07:00', '09:30', 1, 'DA_KET_THUC', 'Buoi 1 - Gioi thieu mon hoc'),
    (102, 101, '2025-09-15', '07:00', '09:30', 2, 'DA_KET_THUC', 'Buoi 2 - Mo hinh ERD'),
    (103, 102, '2025-09-10', '09:45', '12:15', 1, 'DA_KET_THUC', 'Buoi 1 - HTML CSS'),
    (104, 103, '2025-09-12', '13:00', '15:30', 1, 'DA_KET_THUC', 'Buoi 1 - Tong quan AI'),
    (105, 103, '2025-09-19', '13:00', '15:30', 2, 'DANG_MO', 'Buoi 2 - Hoc may co ban')
) AS v(ma_buoi_hoc, ma_lop_hoc_phan, ngay_hoc, gio_bat_dau, gio_ket_thuc, so_buoi, trang_thai, ghi_chu)
WHERE NOT EXISTS (SELECT 1 FROM buoihoc b WHERE b.ma_buoi_hoc = v.ma_buoi_hoc);

INSERT INTO diemdanh (ma_diem_danh, ma_sinh_vien, ma_buoi_hoc, trang_thai, phuong_thuc, do_tin_cay, thoi_diem_diem_danh, ly_do_chinh_sua)
SELECT v.ma_diem_danh, v.ma_sinh_vien, v.ma_buoi_hoc, v.trang_thai, v.phuong_thuc, v.do_tin_cay, v.thoi_diem_diem_danh::timestamp, v.ly_do_chinh_sua
FROM (VALUES
    (101, 101, 101, 'CO_MAT', 'KHUON_MAT', 0.96, '2025-09-08 07:03:00', NULL),
    (102, 102, 101, 'DI_MUON', 'KHUON_MAT', 0.91, '2025-09-08 07:18:00', NULL),
    (103, 103, 101, 'VANG', 'THU_CONG', NULL, NULL, NULL),
    (104, 101, 102, 'CO_MAT', 'KHUON_MAT', 0.94, '2025-09-15 07:05:00', NULL),
    (105, 102, 102, 'VANG', 'THU_CONG', NULL, NULL, NULL),
    (106, 103, 102, 'CO_MAT', 'KHUON_MAT', 0.90, '2025-09-15 07:08:00', NULL),
    (107, 101, 103, 'CO_MAT', 'KHUON_MAT', 0.93, '2025-09-10 09:50:00', NULL),
    (108, 102, 103, 'CO_MAT', 'KHUON_MAT', 0.97, '2025-09-10 09:48:00', NULL),
    (109, 102, 104, 'DI_MUON', 'KHUON_MAT', 0.88, '2025-09-12 13:21:00', NULL),
    (110, 103, 104, 'CO_MAT', 'KHUON_MAT', 0.92, '2025-09-12 13:02:00', NULL)
) AS v(ma_diem_danh, ma_sinh_vien, ma_buoi_hoc, trang_thai, phuong_thuc, do_tin_cay, thoi_diem_diem_danh, ly_do_chinh_sua)
WHERE NOT EXISTS (
    SELECT 1 FROM diemdanh d
    WHERE d.ma_sinh_vien = v.ma_sinh_vien
      AND d.ma_buoi_hoc = v.ma_buoi_hoc
);

INSERT INTO khieunai (ma_khieu_nai, ma_diem_danh, ma_sinh_vien, ly_do, trang_thai, ma_can_bo_xu_ly, ghi_chu_xu_ly, ngay_xu_ly, ngay_gui, duong_dan_minh_chung)
SELECT 101, 103, 103, 'Em co mat trong lop nhung he thong chua ghi nhan diem danh.', 'CHO_XU_LY', NULL, NULL, NULL, NOW(), NULL
WHERE NOT EXISTS (SELECT 1 FROM khieunai WHERE ma_khieu_nai = 101);

INSERT INTO khieunai (ma_khieu_nai, ma_diem_danh, ma_sinh_vien, ly_do, trang_thai, ma_can_bo_xu_ly, ghi_chu_xu_ly, ngay_xu_ly, ngay_gui, duong_dan_minh_chung)
SELECT 102, 105, 102, 'Em co vao lop muon 5 phut nhung bi ghi vang.', 'DA_DUYET', 101, 'Da doi chieu camera va chap thuan.', NOW(), NOW() - INTERVAL '1 day', NULL
WHERE NOT EXISTS (SELECT 1 FROM khieunai WHERE ma_khieu_nai = 102);

INSERT INTO anhkhuonmat (ma_anh, ma_sinh_vien, duong_dan_anh, loai_anh, embedding_vector)
SELECT v.ma_anh, v.ma_sinh_vien, v.duong_dan_anh, 'CHINH_DIEN', NULL
FROM (VALUES
    (101, 101, 'uploads/faces/sv001_main.jpg'),
    (102, 102, 'uploads/faces/sv002_main.jpg'),
    (103, 103, 'uploads/faces/sv003_main.jpg')
) AS v(ma_anh, ma_sinh_vien, duong_dan_anh)
WHERE NOT EXISTS (SELECT 1 FROM anhkhuonmat a WHERE a.ma_anh = v.ma_anh);

INSERT INTO anhdiemdanh (ma_anh, ma_diem_danh, duong_dan_anh, ngay_tao)
SELECT v.ma_anh, v.ma_diem_danh, v.duong_dan_anh, NOW()
FROM (VALUES
    (101, 101, 'uploads/attendance/dd101.jpg'),
    (102, 102, 'uploads/attendance/dd102.jpg'),
    (103, 104, 'uploads/attendance/dd104.jpg')
) AS v(ma_anh, ma_diem_danh, duong_dan_anh)
WHERE NOT EXISTS (SELECT 1 FROM anhdiemdanh a WHERE a.ma_anh = v.ma_anh);

INSERT INTO lichsudiemdanh (ma_lich_su, ma_diem_danh, ma_can_bo, trang_thai_cu, trang_thai_moi, ly_do, thoi_gian)
SELECT 101, 105, 101, 'VANG', 'CO_MAT', 'Chap thuan khieu nai cua sinh vien', NOW()
WHERE NOT EXISTS (SELECT 1 FROM lichsudiemdanh WHERE ma_lich_su = 101);

INSERT INTO nhatkyhethong (ma_nhat_ky, ma_tai_khoan, hanh_dong, doi_tuong, doi_tuong_id, du_lieu_cu, du_lieu_moi, thoi_gian)
SELECT 101, 101, 'SEED_SAMPLE_DATA', 'DATABASE', 'render-sample', NULL, 'Them du lieu mau phuc vu demo va kiem thu', NOW()
WHERE NOT EXISTS (SELECT 1 FROM nhatkyhethong WHERE ma_nhat_ky = 101);

SELECT setval(pg_get_serial_sequence('nganh', 'ma_nganh'), GREATEST((SELECT MAX(ma_nganh) FROM nganh), 1), true);
SELECT setval(pg_get_serial_sequence('taikhoan', 'ma_tai_khoan'), GREATEST((SELECT MAX(ma_tai_khoan) FROM taikhoan), 1), true);
SELECT setval(pg_get_serial_sequence('canbo', 'ma_can_bo'), GREATEST((SELECT MAX(ma_can_bo) FROM canbo), 1), true);
SELECT setval(pg_get_serial_sequence('sinhvien', 'ma_sinh_vien'), GREATEST((SELECT MAX(ma_sinh_vien) FROM sinhvien), 1), true);
SELECT setval(pg_get_serial_sequence('lophocphan', 'ma_lop_hoc_phan'), GREATEST((SELECT MAX(ma_lop_hoc_phan) FROM lophocphan), 1), true);
SELECT setval(pg_get_serial_sequence('buoihoc', 'ma_buoi_hoc'), GREATEST((SELECT MAX(ma_buoi_hoc) FROM buoihoc), 1), true);
SELECT setval(pg_get_serial_sequence('thoikhoabieu', 'ma_thoi_khoa_bieu'), GREATEST((SELECT MAX(ma_thoi_khoa_bieu) FROM thoikhoabieu), 1), true);
SELECT setval(pg_get_serial_sequence('diemdanh', 'ma_diem_danh'), GREATEST((SELECT MAX(ma_diem_danh) FROM diemdanh), 1), true);
SELECT setval(pg_get_serial_sequence('khieunai', 'ma_khieu_nai'), GREATEST((SELECT MAX(ma_khieu_nai) FROM khieunai), 1), true);
SELECT setval(pg_get_serial_sequence('anhkhuonmat', 'ma_anh'), GREATEST((SELECT MAX(ma_anh) FROM anhkhuonmat), 1), true);
SELECT setval(pg_get_serial_sequence('anhdiemdanh', 'ma_anh'), GREATEST((SELECT MAX(ma_anh) FROM anhdiemdanh), 1), true);
SELECT setval(pg_get_serial_sequence('lichsudiemdanh', 'ma_lich_su'), GREATEST((SELECT MAX(ma_lich_su) FROM lichsudiemdanh), 1), true);
SELECT setval(pg_get_serial_sequence('nhatkyhethong', 'ma_nhat_ky'), GREATEST((SELECT MAX(ma_nhat_ky) FROM nhatkyhethong), 1), true);

COMMIT;
