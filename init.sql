-- ===========================================================================
-- SEED DATA FOR AI FACE ATTENDANCE SYSTEM
-- ===========================================================================
-- NOTE: This script runs ONLY when the database is first created (fresh volume).
-- Tables are created by Alembic migrations, NOT by this script.
-- This script will safely skip if tables don't exist yet.
-- After first boot, run: alembic upgrade head && psql -f init.sql
-- ===========================================================================

-- Enable pgvector extension (required for face embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

/* =========================================================
   SEED DATA (only runs if schema already exists)
   ========================================================= */

DO $$
BEGIN
    -- Check if schema has been created by Alembic (check for accounts table)
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'accounts') THEN
        RAISE NOTICE 'Tables not yet created. Skipping seed data — run Alembic migrations first.';
        RETURN;
    END IF;

    -- Reset existing data (safe for re-seeding)
    TRUNCATE TABLE
        attendance_images,
        face_images,
        course_registrations,
        appeals,
        attendance,
        class_sessions,
        timetables,
        class_sections,
        courses,
        students,
        staff,
        refresh_token,
        oauth_identity,
        accounts,
        majors
    RESTART IDENTITY CASCADE;

    -- MAJORS (NGÀNH)
    INSERT INTO majors (major_name, description)
    VALUES ('Công nghệ thông tin', 'Ngành CNTT');

    -- ACCOUNTS (TÀI KHOẢN)
    INSERT INTO accounts (username, password_hash, role, status, failed_login_count, locked_until, created_at)
    VALUES
    ('admin@university.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'ADMIN', true, 0, NULL, NOW()),
    ('gv001@university.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'GIANG_VIEN', true, 0, NULL, NOW()),
    ('sv001@student.edu.vn', '$2b$12$6dCSBvs52cfB14dAASubu.Px4/yiAFg.9yiTHieAKFeVk/C9oP1Lu', 'SINH_VIEN', true, 0, NULL, NOW());

    -- STAFF (CÁN BỘ)
    INSERT INTO staff (last_name, first_name, phone, gender, birth_date, google_email, account_id, position, status)
    VALUES (
        'Nguyễn', 'Văn A', '0909000001', 'Nam', '1985-05-20', 'gva@university.edu.vn',
        (SELECT account_id FROM accounts WHERE username = 'gv001@university.edu.vn'),
        'Giảng viên', true
    );

    -- STUDENTS (SINH VIÊN)
    INSERT INTO students (last_name, first_name, birth_date, gender, phone, google_email, major_id, account_id, academic_status, study_started_at)
    VALUES (
        'Trần', 'Văn B', '2004-03-12', 'Nam', '0911111111', 'sv001@student.edu.vn',
        (SELECT major_id FROM majors LIMIT 1),
        (SELECT account_id FROM accounts WHERE username = 'sv001@student.edu.vn'),
        true, NOW()
    );

    -- COURSES (HỌC PHẦN)
    INSERT INTO courses (course_id, course_name, description, credit_count, status)
    VALUES (101, 'Cơ sở dữ liệu', 'Môn học SQL', 3, true);

    -- CLASS_SECTIONS (LỚP HỌC PHẦN)
    INSERT INTO class_sections (course_id, staff_id, semester, academic_year, minimum_attendance_rate, status, created_at)
    VALUES (
        101,
        (SELECT staff_id FROM staff LIMIT 1),
        1, '2025-2026', 0.8, true, NOW()
    );

    -- CLASS_SESSIONS (BUỔI HỌC)
    INSERT INTO class_sessions (class_section_id, class_date, start_time, end_time, session_number, status, recognition_threshold, late_grace_minutes, note)
    VALUES (
        (SELECT class_section_id FROM class_sections LIMIT 1),
        '2025-09-08', '07:00', '09:30', 1, 'DA_KET_THUC', 0.5, 15, 'Buổi học đầu tiên'
    );

    -- ATTENDANCE (ĐIỂM DANH)
    INSERT INTO attendance (student_id, class_session_id, status, method, confidence, attended_at)
    VALUES (
        (SELECT student_id FROM students LIMIT 1),
        (SELECT class_session_id FROM class_sessions LIMIT 1),
        'CO_MAT', 'KHUON_MAT', 0.95, NOW()
    );

    -- APPEALS (KHIẾU NẠI)
    INSERT INTO appeals (attendance_id, student_id, reason, status, submitted_at, resolver_id, resolution_note, resolved_at)
    VALUES (
        (SELECT attendance_id FROM attendance LIMIT 1),
        (SELECT student_id FROM students LIMIT 1),
        'Em vào lớp đúng giờ nhưng hệ thống nhận diện chậm',
        'DA_DUYET', NOW(),
        (SELECT staff_id FROM staff LIMIT 1),
        'Đã kiểm tra camera', NOW()
    );

    RAISE NOTICE 'Seed data inserted successfully!';
END $$;
