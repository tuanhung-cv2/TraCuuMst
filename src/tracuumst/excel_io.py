from pathlib import Path

import pandas as pd

from .models import LookupRecord, LookupResult, TrangThai


def doc_input(path: str, sheet: str, column: str) -> list[LookupRecord]:
    """Đọc danh sách CCCD/CMND từ file Excel, chuẩn hoá và loại trùng/rỗng."""
    df = pd.read_excel(path, sheet_name=sheet, dtype=str)
    ban_ghi: list[LookupRecord] = []
    da_thay: set[str] = set()

    for dong_goc, gia_tri in enumerate(df[column], start=2):  # dòng 1 là header trong Excel
        if gia_tri is None:
            continue
        cccd = str(gia_tri).strip()
        if not cccd or cccd.lower() == "nan":
            continue
        if cccd in da_thay:
            continue
        da_thay.add(cccd)
        ban_ghi.append(LookupRecord(cccd=cccd, dong_goc=dong_goc))

    return ban_ghi


def _gia_tri_hoac_none(hang: pd.Series, cot: str):
    gia_tri = hang.get(cot)
    return None if pd.isna(gia_tri) else gia_tri


def doc_ket_qua_da_co(output_path: str) -> dict[str, LookupResult]:
    """Trả về dict {CCCD: LookupResult} cho các bản ghi đã 'Thành công' ở file output cũ
    (phục vụ FR-08 / BR-Rule-03). Trả về kết quả đầy đủ (không chỉ tập CCCD) để có thể
    giữ lại nguyên vẹn các bản ghi này khi ghi đè file output ở lần chạy tiếp theo."""
    if not Path(output_path).exists():
        return {}
    df = pd.read_excel(output_path, dtype=str)
    if "CCCD/CMND" not in df.columns or "Trạng thái" not in df.columns:
        return {}

    da_xong: dict[str, LookupResult] = {}
    for _, hang in df.iterrows():
        if hang.get("Trạng thái") != TrangThai.THANH_CONG.value:
            continue
        cccd = hang["CCCD/CMND"]
        so_lan = _gia_tri_hoac_none(hang, "Số lần thử CAPTCHA")
        da_xong[cccd] = LookupResult(
            cccd=cccd,
            trang_thai=TrangThai.THANH_CONG,
            mst=_gia_tri_hoac_none(hang, "MST"),
            ho_ten=_gia_tri_hoac_none(hang, "Họ tên"),
            dia_chi=_gia_tri_hoac_none(hang, "Địa chỉ"),
            co_quan_thue=_gia_tri_hoac_none(hang, "Cơ quan thuế quản lý"),
            so_lan_thu_captcha=int(float(so_lan)) if so_lan is not None else 0,
            ghi_chu=_gia_tri_hoac_none(hang, "Ghi chú"),
        )
    return da_xong


def ghi_ket_qua(ket_qua: list[LookupResult], output_path: str) -> None:
    df = pd.DataFrame([{
        "CCCD/CMND": r.cccd,
        "MST": r.mst,
        "Họ tên": r.ho_ten,
        "Địa chỉ": r.dia_chi,
        "Cơ quan thuế quản lý": r.co_quan_thue,
        "Trạng thái": r.trang_thai.value,
        "Số lần thử CAPTCHA": r.so_lan_thu_captcha,
        "Ghi chú": r.ghi_chu,
    } for r in ket_qua])
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
        _dat_dinh_dang_text(writer, df, cot_can_giu_so_0=["CCCD/CMND", "MST"])


def _dat_dinh_dang_text(writer: pd.ExcelWriter, df: pd.DataFrame, cot_can_giu_so_0: list[str]) -> None:
    """Ép định dạng cell dạng Text ('@') cho các cột chứa số nhưng cần giữ nguyên số 0 ở đầu
    (CCCD/MST), tránh Excel tự hiển thị/diễn giải lại thành số khi mở file."""
    worksheet = writer.sheets[list(writer.sheets.keys())[0]]
    for ten_cot in cot_can_giu_so_0:
        if ten_cot not in df.columns:
            continue
        chi_so_cot = df.columns.get_loc(ten_cot) + 1  # openpyxl đánh số cột từ 1
        for dong in range(2, len(df) + 2):  # dòng 1 là header
            worksheet.cell(row=dong, column=chi_so_cot).number_format = "@"
