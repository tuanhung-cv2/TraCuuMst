from dataclasses import dataclass
from enum import Enum


class TrangThai(str, Enum):
    THANH_CONG = "Thành công"
    KHONG_TIM_THAY = "Không tìm thấy"
    LOI = "Lỗi"
    DINH_DANG_KHONG_HOP_LE = "Định dạng không hợp lệ"


@dataclass
class LookupRecord:
    """Một dòng đầu vào cần tra cứu."""
    cccd: str
    dong_goc: int  # số thứ tự dòng trong Excel gốc, phục vụ resume/log


@dataclass
class LookupResult:
    cccd: str
    trang_thai: TrangThai
    mst: str | None = None
    ho_ten: str | None = None
    dia_chi: str | None = None
    co_quan_thue: str | None = None
    so_lan_thu_captcha: int = 0
    ghi_chu: str | None = None
