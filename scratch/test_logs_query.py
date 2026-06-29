import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sqlmodel import Session, select, func
from app.core.db import engine
from app.models import AuditLog

def main():
    with Session(engine) as session:
        logs = session.exec(select(AuditLog).order_by(AuditLog.timestamp.desc())).all()
        print(f"Total AuditLogs in DB: {len(logs)}")
        for l in logs[:10]:
            print(f"Log ID: {l.audit_log_id} | Action: {l.action} | Account: {l.account_id} | TS: {l.timestamp}")

if __name__ == "__main__":
    main()
