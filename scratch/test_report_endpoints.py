import sys
from sqlmodel import Session, select
from app.core.db import engine
from app.models import Account
from app.services import staff_service

def test_endpoints():
    with Session(engine) as session:
        acc = session.exec(select(Account).where(Account.username == "gv2101")).first()
        if not acc:
            print("ERROR: gv2101 not found!")
            return
        
        print(f"Testing for Account ID: {acc.account_id} (gv2101)")
        
        # 1. Test read_my_class_sections
        my_classes_res = staff_service.read_my_class_sections(session=session, account_id=acc.account_id)
        print("\n=== 1. GET /staff/me/class-sections ===")
        print("Count:", my_classes_res.get("count", 0))
        for item in my_classes_res.get("data", []):
            print(f" -> ClassSection ID: {item.get('class_section_id')} | Students: {item.get('current_students')}")

        # 2. Test read_my_reports
        reports_res = staff_service.read_my_reports(session=session, account_id=acc.account_id)
        print("\n=== 2. GET /staff/me/reports ===")
        print("Reports count:", len(reports_res))
        for r in reports_res:
            print(f" -> Report ID: {r.get('id')} | Total Students: {r.get('totalStudents')} | Avg Rate: {r.get('averageAttendanceRate')}%")
            print(f"    Data Points count: {len(r.get('dataPoints', []))}")

if __name__ == "__main__":
    test_endpoints()
