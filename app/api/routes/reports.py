import io
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.api.deps import (
    CurrentAccount,
    SessionDep,
    get_current_active_lecturer,
)
from app.services.attendance_summary_service import get_attendance_report_df

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/class-sections/{class_section_id}/attendance",
    dependencies=[Depends(get_current_active_lecturer)],
)
def export_attendance_report(
    session: SessionDep,
    current_account: CurrentAccount,
    class_section_id: int,
    format: str = Query(default="xlsx", pattern="^(xlsx|csv)$"),
) -> Any:
    """Giảng viên xuất file Excel điểm danh của lớp học phần."""
    if format == "csv":
        return _build_attendance_csv_response(
            session=session,
            current_account=current_account,
            class_section_id=class_section_id,
        )

    df, _ = get_attendance_report_df(
        session=session,
        current_account=current_account,
        class_section_id=class_section_id,
        unsigned=False,
    )

    # Chuyển DataFrame thành file Excel trong bộ nhớ
    import pandas as pd

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
    output.seek(0)

    # Đặt tên file
    filename = f"DiemDanh_{class_section_id}.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        output,
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def _build_attendance_csv_response(
    session: SessionDep,
    current_account: CurrentAccount,
    class_section_id: int,
) -> Any:
    """Giang vien xuat file CSV diem danh cua lop hoc phan."""
    df, _ = get_attendance_report_df(
        session=session,
        current_account=current_account,
        class_section_id=class_section_id,
        unsigned=True,
    )

    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_bytes = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    filename = f"DiemDanh_{class_section_id}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(csv_bytes, headers=headers, media_type="text/csv")
