import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tracuumst import gdt_client
from tracuumst.captcha_solver import CaptchaError
from tracuumst.config import Config
from tracuumst.gdt_client import RateLimitError
from tracuumst.models import LookupResult, TrangThai


def _cau_hinh_test(**overrides) -> Config:
    mac_dinh = dict(
        input="input/danh_sach_cccd.xlsx", sheet="DanhSachCCCD", column="CCCD",
        output="output/ket_qua_tra_cuu.xlsx", delay=0, max_retry_network=2,
        max_retry_captcha=3, timeout=15, headless=True, log_file="tra_cuu.log",
    )
    mac_dinh.update(overrides)
    return Config(**mac_dinh)


def test_captcha_loi_lien_tuc_gan_khong_tim_thay(monkeypatch):
    """FR-11/BR-Rule-04: CAPTCHA sai liên tục sau max_retry_captcha lần -> 'Không tìm thấy'
    (không phải 'Lỗi', vì trang không phân biệt được sai CAPTCHA với không tìm thấy dữ liệu -
    xem docs/tai-lieu-thiet-ke-ky-thuat.md mục 7.2/14)."""
    cfg = _cau_hinh_test(max_retry_captcha=3)

    def _gia_lap_tra_cuu(driver, solver, cccd, max_retry_captcha):
        raise CaptchaError(f"Không có bảng kết quả sau {max_retry_captcha} lần thử")

    monkeypatch.setattr(gdt_client, "tra_cuu", _gia_lap_tra_cuu)

    ket_qua = gdt_client.tra_cuu_voi_retry(driver=None, solver=None, cccd="123456789012", cfg=cfg)

    assert ket_qua.trang_thai == TrangThai.KHONG_TIM_THAY
    assert ket_qua.so_lan_thu_captcha == cfg.max_retry_captcha
    assert ket_qua.ghi_chu is not None


def test_thanh_cong_tra_ve_ket_qua_dung(monkeypatch):
    cfg = _cau_hinh_test()

    def _gia_lap_tra_cuu(driver, solver, cccd, max_retry_captcha):
        return "<html></html>", 1

    def _gia_lap_parse(html, cccd):
        return LookupResult(cccd=cccd, trang_thai=TrangThai.THANH_CONG, mst="8888888888")

    monkeypatch.setattr(gdt_client, "tra_cuu", _gia_lap_tra_cuu)
    monkeypatch.setattr(gdt_client.result_parser, "parse", _gia_lap_parse)

    ket_qua = gdt_client.tra_cuu_voi_retry(driver=None, solver=None, cccd="123456789012", cfg=cfg)

    assert ket_qua.trang_thai == TrangThai.THANH_CONG
    assert ket_qua.mst == "8888888888"
    assert ket_qua.so_lan_thu_captcha == 1


def test_loi_ket_noi_thu_lai_roi_gan_loi(monkeypatch):
    cfg = _cau_hinh_test(max_retry_network=2)
    so_lan_goi = {"count": 0}

    def _gia_lap_tra_cuu(driver, solver, cccd, max_retry_captcha):
        so_lan_goi["count"] += 1
        from selenium.common.exceptions import TimeoutException
        raise TimeoutException("gia lap loi mang")

    monkeypatch.setattr(gdt_client, "tra_cuu", _gia_lap_tra_cuu)
    monkeypatch.setattr(time, "sleep", lambda *_: None)  # bỏ qua chờ thật trong test

    ket_qua = gdt_client.tra_cuu_voi_retry(driver=None, solver=None, cccd="123456789012", cfg=cfg)

    assert ket_qua.trang_thai == TrangThai.LOI
    assert so_lan_goi["count"] == cfg.max_retry_network


def test_rate_limit_nghi_lau_hon_roi_thanh_cong(monkeypatch):
    cfg = _cau_hinh_test(max_retry_network=2, delay=1)
    lan_goi = {"count": 0}

    def _gia_lap_tra_cuu(driver, solver, cccd, max_retry_captcha):
        lan_goi["count"] += 1
        if lan_goi["count"] == 1:
            raise RateLimitError("Too Many Requests")
        return "<html></html>", 1

    def _gia_lap_parse(html, cccd):
        return LookupResult(cccd=cccd, trang_thai=TrangThai.THANH_CONG, mst="1111111111")

    monkeypatch.setattr(gdt_client, "tra_cuu", _gia_lap_tra_cuu)
    monkeypatch.setattr(gdt_client.result_parser, "parse", _gia_lap_parse)
    monkeypatch.setattr(time, "sleep", lambda *_: None)

    ket_qua = gdt_client.tra_cuu_voi_retry(driver=None, solver=None, cccd="123456789012", cfg=cfg)

    assert ket_qua.trang_thai == TrangThai.THANH_CONG
    assert lan_goi["count"] == 2
