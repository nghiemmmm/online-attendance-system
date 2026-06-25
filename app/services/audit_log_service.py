from typing import Any

from fastapi import Request
from sqlmodel import Session, func, select

from app.models import AuditLog, AuditLogsPublic, TaiKhoan


def request_ip(request: Request | None) -> str | None:
    if not request or not request.client:
        return None
    return request.client.host


def request_user_agent(request: Request | None) -> str | None:
    if not request:
        return None
    return request.headers.get("user-agent")


def write_audit_log(
    *,
    session: Session,
    account: TaiKhoan | None = None,
    hanh_dong: str,
    doi_tuong: str | None = None,
    doi_tuong_id: str | int | None = None,
    du_lieu_truoc: dict[str, Any] | None = None,
    du_lieu_sau: dict[str, Any] | None = None,
    request: Request | None = None,
    trang_thai: str = "SUCCESS",
    chi_tiet: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        ma_tai_khoan=account.ma_tai_khoan if account else None,
        vai_tro=account.vai_tro if account else None,
        hanh_dong=hanh_dong,
        doi_tuong=doi_tuong,
        doi_tuong_id=str(doi_tuong_id) if doi_tuong_id is not None else None,
        du_lieu_truoc=du_lieu_truoc,
        du_lieu_sau=du_lieu_sau,
        ip=request_ip(request),
        user_agent=request_user_agent(request),
        trang_thai=trang_thai,
        chi_tiet=chi_tiet,
    )
    session.add(audit_log)
    session.commit()
    session.refresh(audit_log)
    return audit_log


def read_audit_logs(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    hanh_dong: str | None = None,
    doi_tuong: str | None = None,
    ma_tai_khoan: int | None = None,
) -> AuditLogsPublic:
    count_statement = select(func.count()).select_from(AuditLog)
    statement = select(AuditLog)

    if hanh_dong:
        count_statement = count_statement.where(AuditLog.hanh_dong == hanh_dong)
        statement = statement.where(AuditLog.hanh_dong == hanh_dong)
    if doi_tuong:
        count_statement = count_statement.where(AuditLog.doi_tuong == doi_tuong)
        statement = statement.where(AuditLog.doi_tuong == doi_tuong)
    if ma_tai_khoan:
        count_statement = count_statement.where(AuditLog.ma_tai_khoan == ma_tai_khoan)
        statement = statement.where(AuditLog.ma_tai_khoan == ma_tai_khoan)

    count = session.exec(count_statement).one()
    items = session.exec(
        statement.order_by(AuditLog.thoi_gian.desc()).offset(skip).limit(limit)
    ).all()
    return AuditLogsPublic(data=items, count=count)
