"""OTP verification service for student registration."""

import random
import logging
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select, col
from fastapi import HTTPException

from app.models import Student, Account, OTPRecord
from app.utils import send_email, EmailData
from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_and_send_otp(*, session: Session, mssv: int, email: str) -> dict[str, str]:
    """Check student eligibility and send OTP verification code."""
    # 1. Check if student exists with given MSSV
    student = session.get(Student, mssv)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy mã sinh viên {mssv} trong hệ thống",
        )

    # 2. Verify email matches student record (or update if not set)
    if student.google_email:
        if student.google_email.strip().lower() != email.strip().lower():
            raise HTTPException(
                status_code=400,
                detail=f"Email nhập vào ({email}) không trùng khớp với Email sinh viên trong hệ thống ({student.google_email})",
            )
    else:
        # If student record has no pre-filled email, set it to the provided email
        student.google_email = email.strip().lower()
        session.add(student)
        session.commit()

    # 3. Check if student already has an linked account
    if student.account_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Mã sinh viên này đã đăng ký tài khoản trước đó",
        )

    # 4. Generate 6-digit OTP code
    otp_code = f"{random.randint(100000, 999999)}"
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=5)

    # Store OTP in DB
    otp_record = OTPRecord(
        email=email.strip().lower(),
        code=otp_code,
        expires_at=expires_at,
        is_used=False,
    )
    session.add(otp_record)
    session.commit()

    # 5. Send Email
    subject = "Mã xác thực đăng ký tài khoản Điểm Danh"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Xác thực đăng ký tài khoản</h2>
        <p>Mã OTP xác thực của bạn là: <strong style="font-size: 24px; color: #0EA5E9;">{otp_code}</strong></p>
        <p>Mã có hiệu lực trong vòng 5 phút. Vui lòng không chia sẻ mã này với bất kỳ ai.</p>
    </div>
    """
    try:
        if settings.emails_enabled:
            send_email(email_to=email, subject=subject, html_content=html_content)
            logger.info("OTP sent successfully to %s", email)
        else:
            logger.warning("[DEV MODE] Email disabled. OTP for %s is %s", email, otp_code)
    except Exception as e:
        logger.error("Failed to send OTP email: %s. OTP code was %s", str(e), otp_code)

    return {"message": f"Mã OTP đã được gửi tới email {email}", "dev_otp": otp_code if not settings.emails_enabled else None}


def verify_otp(*, session: Session, email: str, code: str) -> bool:
    """Verify if the OTP code is valid and active."""
    now = datetime.now(timezone.utc)
    statement = (
        select(OTPRecord)
        .where(OTPRecord.email == email.strip().lower())
        .where(OTPRecord.code == code.strip())
        .where(OTPRecord.is_used == False)
        .where(OTPRecord.expires_at > now)
        .order_by(col(OTPRecord.created_at).desc())
    )
    otp_record = session.exec(statement).first()
    if not otp_record:
        return False

    otp_record.is_used = True
    session.add(otp_record)
    session.commit()
    return True
