import io
import pandas as pd
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.api.deps import SessionDep, get_current_active_lecturer, get_current_active_superuser, CurrentAccount
from app.models import LopHocPhan, BuoiHoc, DiemDanh, SinhVien, DangKyHocPhan, CanBo
from app.crud import canbo_crud
from app.services.attendance_summary_service import get_attendance_report_df

router = APIRouter(prefix="/bao-cao", tags=["bao-cao"])

@router.get("/lop-hoc-phan/{ma_lop_hoc_phan}/export-excel", dependencies=[Depends(get_current_active_lecturer)])
def export_excel_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Giảng viên xuất file Excel điểm danh của lớp học phần."""
    df, _ = get_attendance_report_df(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=ma_lop_hoc_phan,
        unsigned=False,
    )

    # Chuyển DataFrame thành file Excel trong bộ nhớ
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="DiemDanh")
    output.seek(0)

    # Đặt tên file
    filename = f"DiemDanh_{ma_lop_hoc_phan}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }

    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@router.get("/lop-hoc-phan/{ma_lop_hoc_phan}/export-csv", dependencies=[Depends(get_current_active_lecturer)])
def export_csv_diem_danh(
    session: SessionDep,
    current_account: CurrentAccount,
    ma_lop_hoc_phan: int,
) -> Any:
    """Giang vien xuat file CSV diem danh cua lop hoc phan."""
    df, _ = get_attendance_report_df(
        session=session,
        current_account=current_account,
        ma_lop_hoc_phan=ma_lop_hoc_phan,
        unsigned=True,
    )

    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_bytes = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    filename = f"DiemDanh_{ma_lop_hoc_phan}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(csv_bytes, headers=headers, media_type="text/csv")
