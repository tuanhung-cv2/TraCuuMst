import re

PATTERN_CCCD = re.compile(r"^\d{12}$")
PATTERN_CMND = re.compile(r"^\d{9}$")


def kiem_tra_dinh_dang(cccd: str) -> bool:
    """Kiểm tra CCCD (12 số) hoặc CMND (9 số) theo BR-Rule-01."""
    return bool(PATTERN_CCCD.fullmatch(cccd) or PATTERN_CMND.fullmatch(cccd))
