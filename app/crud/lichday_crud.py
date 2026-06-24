from datetime import date

from sqlmodel import Session, select

from app.models import (
    BuoiHoc,
    BuoiHocGanDayItem,
    DiemDanh,
    HocPhan,
    LichDayItem,
    LopHocPhan,
    ThoiKhoaBieu,
)

TRANG_THAI_CO_MAT = "CO_MAT"
TRANG_THAI_DI_MUON = "DI_MUON"
TRANG_THAI_VANG_MAT = {"VANG", "VANG_MAT"}


def get_vietnamese_weekday(value: date) -> int:
    """Chuyển ngày sang thứ kiểu Việt Nam: thứ 2 là 2, chủ nhật là 8."""
    return value.isoweekday() + 1


def infer_current_semester(value: date) -> tuple[int, str]:
    """Suy luận học kỳ và năm học hiện tại từ ngày tham chiếu."""
    if value.month >= 8:
        return 1, f"{value.year}-{value.year + 1}"
    if value.month <= 5:
        return 2, f"{value.year - 1}-{value.year}"
    return 3, f"{value.year - 1}-{value.year}"


def thoi_khoa_bieu_matches_buoi_hoc(
    *, thoi_khoa_bieu: ThoiKhoaBieu, buoi_hoc: BuoiHoc
) -> bool:
    """Kiểm tra thời khóa biểu mẫu có khớp với ngày của buổi học thực tế không."""
    if not (thoi_khoa_bieu.ngay_bat_dau <= buoi_hoc.ngay_hoc <= thoi_khoa_bieu.ngay_ket_thuc):
        return False

    buoi_hoc_thu = get_vietnamese_weekday(buoi_hoc.ngay_hoc)
    return thoi_khoa_bieu.thu in {buoi_hoc_thu, buoi_hoc.ngay_hoc.isoweekday()}


def thoi_khoa_bieu_overlaps_date_range(
    *,
    thoi_khoa_bieu: ThoiKhoaBieu,
    from_date: date | None = None,
    to_date: date | None = None,
) -> bool:
    """Kiểm tra thời khóa biểu mẫu có giao với khoảng ngày lọc không."""
    if from_date and thoi_khoa_bieu.ngay_ket_thuc < from_date:
        return False
    if to_date and thoi_khoa_bieu.ngay_bat_dau > to_date:
        return False
    return True


def build_lich_day_item(
    *,
    lop_hoc_phan: LopHocPhan,
    hoc_phan: HocPhan | None,
    thoi_khoa_bieu: ThoiKhoaBieu | None = None,
    buoi_hoc: BuoiHoc | None = None,
) -> LichDayItem:
    """Ghép dữ liệu lớp học phần, học phần, thời khóa biểu và buổi học thành response."""
    return LichDayItem(
        ma_can_bo=lop_hoc_phan.ma_can_bo,
        ma_lop_hoc_phan=lop_hoc_phan.ma_lop_hoc_phan,
        ma_hoc_phan=lop_hoc_phan.ma_hoc_phan,
        ten_hoc_phan=hoc_phan.ten_hoc_phan if hoc_phan else None,
        ma_thoi_khoa_bieu=(
            thoi_khoa_bieu.ma_thoi_khoa_bieu if thoi_khoa_bieu else None
        ),
        ma_buoi_hoc=buoi_hoc.ma_buoi_hoc if buoi_hoc else None,
        ngay_hoc=buoi_hoc.ngay_hoc if buoi_hoc else None,
        thu=thoi_khoa_bieu.thu if thoi_khoa_bieu else None,
        tiet_bat_dau=thoi_khoa_bieu.tiet_bat_dau if thoi_khoa_bieu else None,
        tiet_ket_thuc=thoi_khoa_bieu.tiet_ket_thuc if thoi_khoa_bieu else None,
        gio_bat_dau=(
            buoi_hoc.gio_bat_dau
            if buoi_hoc and buoi_hoc.gio_bat_dau
            else thoi_khoa_bieu.gio_bat_dau
            if thoi_khoa_bieu
            else None
        ),
        gio_ket_thuc=(
            buoi_hoc.gio_ket_thuc
            if buoi_hoc and buoi_hoc.gio_ket_thuc
            else thoi_khoa_bieu.gio_ket_thuc
            if thoi_khoa_bieu
            else None
        ),
        hoc_ky=lop_hoc_phan.hoc_ky,
        nam_hoc=lop_hoc_phan.nam_hoc,
        trang_thai_lop=lop_hoc_phan.trang_thai,
        trang_thai_buoi_hoc=buoi_hoc.trang_thai if buoi_hoc else None,
        ghi_chu=buoi_hoc.ghi_chu if buoi_hoc else None,
        so_buoi=buoi_hoc.so_buoi if buoi_hoc else None,
    )


def count_diem_danh_by_status(
    *,
    session: Session,
    ma_buoi_hoc: int,
) -> tuple[int, int, int]:
    """Dem so sinh vien co mat, di muon va vang mat theo mot buoi hoc."""
    trang_thais = session.exec(
        select(DiemDanh.trang_thai).where(DiemDanh.ma_buoi_hoc == ma_buoi_hoc)
    ).all()

    so_co_mat = sum(1 for trang_thai in trang_thais if trang_thai == TRANG_THAI_CO_MAT)
    so_di_muon = sum(1 for trang_thai in trang_thais if trang_thai == TRANG_THAI_DI_MUON)
    so_vang_mat = sum(1 for trang_thai in trang_thais if trang_thai in TRANG_THAI_VANG_MAT)
    return so_co_mat, so_di_muon, so_vang_mat


def get_buoi_hoc_gan_day_by_can_bo(
    *,
    session: Session,
    ma_can_bo: int,
    limit: int = 5,
) -> tuple[list[BuoiHocGanDayItem], int]:
    """Lay danh sach buoi hoc gan day cua can bo kem thong ke diem danh."""
    statement = (
        select(BuoiHoc)
        .join(LopHocPhan, BuoiHoc.ma_lop_hoc_phan == LopHocPhan.ma_lop_hoc_phan)
        .where(LopHocPhan.ma_can_bo == ma_can_bo)
        .order_by(BuoiHoc.ngay_hoc.desc(), BuoiHoc.ma_buoi_hoc.desc())
        .limit(limit)
    )
    buoi_hocs = session.exec(statement).all()
    items: list[BuoiHocGanDayItem] = []

    for buoi_hoc in buoi_hocs:
        lop_hoc_phan = session.get(LopHocPhan, buoi_hoc.ma_lop_hoc_phan)
        hoc_phan = (
            session.get(HocPhan, lop_hoc_phan.ma_hoc_phan)
            if lop_hoc_phan
            else None
        )
        so_co_mat, so_di_muon, so_vang_mat = count_diem_danh_by_status(
            session=session,
            ma_buoi_hoc=buoi_hoc.ma_buoi_hoc,
        )
        items.append(
            BuoiHocGanDayItem(
                ma_lop_hoc_phan=buoi_hoc.ma_lop_hoc_phan,
                ten_hoc_phan=hoc_phan.ten_hoc_phan if hoc_phan else None,
                ngay_hoc=buoi_hoc.ngay_hoc,
                so_sinh_vien_co_mat=so_co_mat,
                so_sinh_vien_di_muon=so_di_muon,
                so_sinh_vien_vang_mat=so_vang_mat,
            )
        )

    return items, len(items)


def get_lich_day_by_can_bo(
    *,
    session: Session,
    ma_can_bo: int,
    from_date: date | None = None,
    to_date: date | None = None,
    hoc_ky: int | None = None,
    nam_hoc: str | None = None,
    trang_thai: bool | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[LichDayItem], int]:
    """
    Lấy lịch dạy của cán bộ từ lớp học phần, thời khóa biểu và buổi học.

    Nếu lớp có buổi học thực tế, mỗi buổi học là một dòng lịch. Nếu lớp chưa có buổi
    học, hàm trả về các dòng thời khóa biểu mẫu còn giao với khoảng ngày lọc.
    """
    lop_statement = select(LopHocPhan).where(LopHocPhan.ma_can_bo == ma_can_bo)
    if hoc_ky is not None:
        lop_statement = lop_statement.where(LopHocPhan.hoc_ky == hoc_ky)
    if nam_hoc:
        lop_statement = lop_statement.where(LopHocPhan.nam_hoc == nam_hoc)
    if trang_thai is not None:
        lop_statement = lop_statement.where(LopHocPhan.trang_thai == trang_thai)

    lop_hoc_phans = session.exec(lop_statement).all()
    items: list[LichDayItem] = []

    for lop_hoc_phan in lop_hoc_phans:
        hoc_phan = session.get(HocPhan, lop_hoc_phan.ma_hoc_phan)

        tkb_statement = select(ThoiKhoaBieu).where(
            ThoiKhoaBieu.ma_lop_hoc_phan == lop_hoc_phan.ma_lop_hoc_phan
        )
        thoi_khoa_bieus = [
            tkb
            for tkb in session.exec(tkb_statement).all()
            if thoi_khoa_bieu_overlaps_date_range(
                thoi_khoa_bieu=tkb,
                from_date=from_date,
                to_date=to_date,
            )
        ]

        buoi_statement = select(BuoiHoc).where(
            BuoiHoc.ma_lop_hoc_phan == lop_hoc_phan.ma_lop_hoc_phan
        )
        if from_date:
            buoi_statement = buoi_statement.where(BuoiHoc.ngay_hoc >= from_date)
        if to_date:
            buoi_statement = buoi_statement.where(BuoiHoc.ngay_hoc <= to_date)
        buoi_hocs = session.exec(buoi_statement.order_by(BuoiHoc.ngay_hoc)).all()

        if buoi_hocs:
            for buoi_hoc in buoi_hocs:
                matched_tkb = next(
                    (
                        tkb
                        for tkb in thoi_khoa_bieus
                        if thoi_khoa_bieu_matches_buoi_hoc(
                            thoi_khoa_bieu=tkb,
                            buoi_hoc=buoi_hoc,
                        )
                    ),
                    None,
                )
                items.append(
                    build_lich_day_item(
                        lop_hoc_phan=lop_hoc_phan,
                        hoc_phan=hoc_phan,
                        thoi_khoa_bieu=matched_tkb,
                        buoi_hoc=buoi_hoc,
                    )
                )
        else:
            for thoi_khoa_bieu in thoi_khoa_bieus:
                items.append(
                    build_lich_day_item(
                        lop_hoc_phan=lop_hoc_phan,
                        hoc_phan=hoc_phan,
                        thoi_khoa_bieu=thoi_khoa_bieu,
                    )
                )

    items.sort(
        key=lambda item: (
            item.ngay_hoc or date.max,
            item.gio_bat_dau or item.gio_ket_thuc,
            item.ma_lop_hoc_phan,
        )
    )
    count = len(items)
    return items[skip : skip + limit], count


def count_lop_hoc_phan_dang_day_by_can_bo(
    *,
    session: Session,
    ma_can_bo: int,
    as_of_date: date,
) -> tuple[int, int, str]:
    """
    Đếm số lớp học phần cán bộ đang giảng dạy trong học kỳ hiện tại.

    Lớp được tính là đang giảng dạy khi thuộc học kỳ/năm học hiện tại, còn hoạt
    động và có thời khóa biểu bao phủ ngày tham chiếu hoặc có buổi học đúng ngày đó.
    """
    hoc_ky, nam_hoc = infer_current_semester(as_of_date)
    lop_statement = select(LopHocPhan).where(
        LopHocPhan.ma_can_bo == ma_can_bo,
        LopHocPhan.hoc_ky == hoc_ky,
        LopHocPhan.nam_hoc == nam_hoc,
        LopHocPhan.trang_thai == True,
    )
    lop_hoc_phans = session.exec(lop_statement).all()
    active_class_ids: set[int] = set()

    for lop_hoc_phan in lop_hoc_phans:
        tkb_statement = select(ThoiKhoaBieu).where(
            ThoiKhoaBieu.ma_lop_hoc_phan == lop_hoc_phan.ma_lop_hoc_phan,
            ThoiKhoaBieu.ngay_bat_dau <= as_of_date,
            ThoiKhoaBieu.ngay_ket_thuc >= as_of_date,
        )
        has_current_tkb = session.exec(tkb_statement).first() is not None

        buoi_statement = select(BuoiHoc).where(
            BuoiHoc.ma_lop_hoc_phan == lop_hoc_phan.ma_lop_hoc_phan,
            BuoiHoc.ngay_hoc == as_of_date,
        )
        has_current_buoi_hoc = session.exec(buoi_statement).first() is not None

        if has_current_tkb or has_current_buoi_hoc:
            active_class_ids.add(lop_hoc_phan.ma_lop_hoc_phan)

    return len(active_class_ids), hoc_ky, nam_hoc
