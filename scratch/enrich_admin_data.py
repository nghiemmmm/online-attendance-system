import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select, text
from app.core.db import engine
from app.models import Account, Student

def main():
    with Session(engine) as session:
        print("Enriching Admin Dashboard data & system logs...")
        
        # Reset auditlog sequence to max + 1
        try:
            session.execute(text("SELECT setval('auditlog_ma_audit_log_seq', (SELECT COALESCE(MAX(ma_audit_log), 0) + 1 FROM auditlog), false);"))
            session.commit()
        except Exception as e:
            print("Seq update warning:", e)
            session.rollback()
        
        # Get password_hash from admin account
        existing_acc = session.exec(select(Account)).first()
        sample_hash = existing_acc.password_hash if existing_acc else "dummy_hash"
        
        # 1. Ensure extra sample accounts / students for rich counts
        extra_students_data = [
            ("21080004", "Vũ Thị Hoa", "hoavt@example.com", "0911223344"),
            ("21080005", "Đặng Văn Minh", "minhdv@example.com", "0922334455"),
            ("21080006", "Bùi Hoàng Nam", "nambh@example.com", "0933445566")
        ]
        
        for mssv, name, email, phone in extra_students_data:
            acc = session.exec(select(Account).where(Account.username == mssv)).first()
            if not acc:
                acc = Account(username=mssv, role="SINH_VIEN", status=True, password_hash=sample_hash)
                session.add(acc)
                session.commit()
                session.refresh(acc)
                
            st = session.exec(select(Student).where(Student.student_id == int(mssv))).first()
            if not st:
                parts = name.split(" ")
                session.add(Student(
                    student_id=int(mssv),
                    account_id=acc.account_id,
                    last_name=" ".join(parts[:-1]),
                    first_name=parts[-1],
                    google_email=email,
                    phone=phone,
                    major_id=1,
                    academic_status=True
                ))
        session.commit()
        
        # 2. Add sample audit logs using raw SQL matching actual DB schema
        admin_acc = session.exec(select(Account).where(Account.role == "ADMIN")).first()
        admin_id = admin_acc.account_id if admin_acc else 1
        
        sample_logs = [
            ("DIEM_DANH_KHUON_MAT", "Attendance", "36", {"student_name": "Nguyễn Đức Nghiêm", "status": "CO_MAT"}, datetime.now(timezone.utc) - timedelta(minutes=15)),
            ("DUYET_KHUON_MAT", "FaceImage", "102", {"student_name": "Trần Thị Mai", "action": "Duyệt ảnh mẫu AI"}, datetime.now(timezone.utc) - timedelta(minutes=45)),
            ("TAO_LOP_HOC_PHAN", "ClassSection", "3", {"course": "Lập trình Di động Flutter", "lecturer": "TS. Nguyễn Văn An"}, datetime.now(timezone.utc) - timedelta(hours=2)),
            ("DANG_NHAP_HE_THONG", "Account", str(admin_id), {"username": "admin", "ip": "127.0.0.1"}, datetime.now(timezone.utc) - timedelta(hours=3)),
            ("DUYET_KHIEU_NAI", "Appeal", "1", {"student": "Nguyễn Đức Nghiêm", "result": "CHAP_NHAN"}, datetime.now(timezone.utc) - timedelta(hours=5))
        ]
        
        insert_query = text("""
            INSERT INTO auditlog (ma_tai_khoan, vai_tro, hanh_dong, doi_tuong, doi_tuong_id, du_lieu_sau, thoi_gian, trang_thai)
            VALUES (:acc_id, 'ADMIN', :action, :target_type, :target_id, :after_data, :ts, 'SUCCESS')
        """)
        
        for action, target_type, target_id, after_data, ts in sample_logs:
            session.execute(insert_query, {
                "acc_id": admin_id,
                "action": action,
                "target_type": target_type,
                "target_id": target_id,
                "after_data": json.dumps(after_data),
                "ts": ts
            })
        session.commit()
        
        print("Admin Dashboard data enrichment completed successfully!")

if __name__ == "__main__":
    main()
