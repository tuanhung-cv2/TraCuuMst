from bs4 import BeautifulSoup

from .models import LookupResult, TrangThai


def parse(html: str, cccd: str) -> LookupResult:
    """Bóc tách bảng kết quả tra cứu. Selector đã xác nhận trên dữ liệu thật (2026-09-19)."""
    soup = BeautifulSoup(html, "html.parser")
    bang_ket_qua = soup.select_one("#resultContainer table.ta_border")

    if bang_ket_qua is None:
        return LookupResult(cccd=cccd, trang_thai=TrangThai.KHONG_TIM_THAY)

    hang_du_lieu = bang_ket_qua.select("tr")[1:]  # bỏ dòng tiêu đề
    if not hang_du_lieu:
        return LookupResult(cccd=cccd, trang_thai=TrangThai.KHONG_TIM_THAY)

    # Cột thực tế: STT, MST, Tên người nộp thuế, Cơ quan thuế quản lý, Trạng thái MST
    # (trang tra cứu cá nhân không trả về địa chỉ)
    cot = [td.get_text(strip=True) for td in hang_du_lieu[0].select("td")]
    return LookupResult(
        cccd=cccd,
        trang_thai=TrangThai.THANH_CONG,
        mst=cot[1] if len(cot) > 1 else None,
        ho_ten=cot[2] if len(cot) > 2 else None,
        dia_chi=None,
        co_quan_thue=cot[3] if len(cot) > 3 else None,
        ghi_chu=cot[4] if len(cot) > 4 else None,  # Trạng thái MST (vd: "NNT đang hoạt động")
    )
