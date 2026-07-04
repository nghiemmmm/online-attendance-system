from typing import Any

from fastapi import Request
from sqlmodel import Session, func, select

from app.models import AuditLog, AuditLogsPublic, Account


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
    account: Account | None = None,
    action: str,
    target_type: str | None = None,
    target_id: str | int | None = None,
    before_data: dict[str, Any] | None = None,
    after_data: dict[str, Any] | None = None,
    request: Request | None = None,
    status: str = "SUCCESS",
    detail: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        ma_tai_khoan=account.account_id if account else None,
        vai_tro=account.role if account else None,
        hanh_dong=action,
        doi_tuong=target_type,
        doi_tuong_id=str(target_id) if target_id is not None else None,
        du_lieu_truoc=before_data,
        du_lieu_sau=after_data,
        ip=request_ip(request),
        user_agent=request_user_agent(request),
        trang_thai=status,
        chi_tiet=detail,
    )
    try:
        session.add(audit_log)
        session.commit()
        session.refresh(audit_log)
    except Exception as e:
        session.rollback()
        import logging
        logging.getLogger("app.audit").error("Failed to write audit log: %s", e)
    return audit_log


def read_audit_logs(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    action: str | None = None,
    target_type: str | None = None,
    account_id: int | None = None,
) -> AuditLogsPublic:
    count_statement = select(func.count()).select_from(AuditLog)
    statement = select(AuditLog)

    if action:
        count_statement = count_statement.where(AuditLog.hanh_dong == action)
        statement = statement.where(AuditLog.hanh_dong == action)
    if target_type:
        count_statement = count_statement.where(AuditLog.doi_tuong == target_type)
        statement = statement.where(AuditLog.doi_tuong == target_type)
    if account_id:
        count_statement = count_statement.where(AuditLog.ma_tai_khoan == account_id)
        statement = statement.where(AuditLog.ma_tai_khoan == account_id)

    count = session.exec(count_statement).one()
    items = session.exec(
        statement.order_by(AuditLog.thoi_gian.desc()).offset(skip).limit(limit)
    ).all()
    return AuditLogsPublic(data=items, count=count)
