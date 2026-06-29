import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.services.cleanup_service import cleanup_expired_attendance_evidence

def main():
    print("Testing Auto-Cleanup Service for attendance evidence images (> 2 days)...")
    count = cleanup_expired_attendance_evidence(days=2)
    print(f"Cleanup finished! Expired images cleaned: {count}")

if __name__ == "__main__":
    main()
