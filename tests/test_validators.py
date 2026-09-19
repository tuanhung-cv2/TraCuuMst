import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tracuumst.validators import kiem_tra_dinh_dang


def test_cccd_hop_le_12_so():
    assert kiem_tra_dinh_dang("001203000001") is True


def test_cmnd_hop_le_9_so():
    assert kiem_tra_dinh_dang("123456789") is True


def test_sai_do_dai():
    assert kiem_tra_dinh_dang("12345") is False
    assert kiem_tra_dinh_dang("1234567890123") is False


def test_co_ky_tu_khong_phai_so():
    assert kiem_tra_dinh_dang("00120300000a") is False


def test_co_khoang_trang_hai_dau_phai_duoc_strip_truoc_khi_kiem_tra():
    # validators.kiem_tra_dinh_dang không tự strip; excel_io chịu trách nhiệm strip trước khi gọi
    assert kiem_tra_dinh_dang(" 001203000001 ") is False
    assert kiem_tra_dinh_dang(" 001203000001 ".strip()) is True


def test_chuoi_rong():
    assert kiem_tra_dinh_dang("") is False


def test_so_bi_ep_kieu_float_tu_excel():
    # Nếu đọc Excel không ép dtype=str, số có thể ra dạng "1203000001.0"
    assert kiem_tra_dinh_dang("1203000001.0") is False
