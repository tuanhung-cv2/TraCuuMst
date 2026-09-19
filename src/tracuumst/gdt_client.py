from __future__ import annotations

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from . import result_parser
from .captcha_solver import CaptchaError, CaptchaSolver
from .config import Config
from .models import LookupResult, TrangThai

logger = logging.getLogger("tracuumst")  # dùng chung logger đã cấu hình trong main.py (file + console)

URL_TRA_CUU = "https://tracuunnt.gdt.gov.vn/tcnnt/mstcn.jsp"
SELECTOR_INPUT_MST = "input[name='mst']"
SELECTOR_CAPTCHA_IMG = "img[src*='captcha.png']"
SELECTOR_INPUT_CAPTCHA = "input#captcha"
SELECTOR_BUTTON_SUBMIT = "input.subBtn"
SELECTOR_RESULT_TABLE = "#resultContainer table.ta_border"


class RateLimitError(Exception):
    """Máy chủ trả về "Too Many Requests" do gửi quá nhiều yêu cầu trong thời gian ngắn
    (phát hiện thực tế khi kiểm thử liên tục ngày 2026-09-19 - xem docs/ke-hoach-trien-khai.md).
    """


def tao_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    # "eager": không chờ tải xong toàn bộ tài nguyên phụ (analytics, font...) mới coi là load xong,
    # tránh treo/timeout khi điều hướng lại trang nhiều lần liên tiếp (đã gặp thực tế khi test retry).
    options.page_load_strategy = "eager"
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def _dien_form(driver: WebDriver, cccd: str) -> None:
    o_mst = driver.find_element("css selector", SELECTOR_INPUT_MST)
    o_mst.clear()
    o_mst.send_keys(cccd)


def _dien_captcha(driver: WebDriver, ma_captcha: str) -> None:
    o_captcha = driver.find_element("css selector", SELECTOR_INPUT_CAPTCHA)
    o_captcha.clear()
    o_captcha.send_keys(ma_captcha)


def _submit(driver: WebDriver) -> None:
    # nút không phải type=submit; site dùng onclick="search()" -> document.myform.submit()
    driver.execute_script("search();")


def _co_bang_ket_qua(driver: WebDriver) -> bool:
    """Trả về True nếu trang có bảng kết quả (CAPTCHA đúng VÀ tìm thấy dữ liệu).

    Lưu ý (xem docs/tai-lieu-thiet-ke-ky-thuat.md mục 7.2): trang KHÔNG phân biệt
    "sai CAPTCHA" và "không tìm thấy dữ liệu" bằng thông báo lỗi -- cả hai đều
    trả về form rỗng. Vì vậy không thể phân biệt hai trường hợp này ở đây.
    """
    phan_tu = driver.find_elements("css selector", SELECTOR_RESULT_TABLE)
    return len(phan_tu) > 0


def _lam_moi_captcha(driver: WebDriver) -> None:
    driver.get(URL_TRA_CUU)
    _cho_trang_san_sang(driver)


def _cho_trang_san_sang(driver: WebDriver, timeout: int = 15) -> None:
    if "Too Many Requests" in driver.page_source:
        raise RateLimitError(
            "Máy chủ trả về 'Too Many Requests' - cần tăng khoảng nghỉ (delay) giữa các lượt tra cứu"
        )
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_INPUT_MST))
    )


def tra_cuu(
    driver: WebDriver,
    solver: CaptchaSolver,
    cccd: str,
    max_retry_captcha: int,
) -> tuple[str, int]:
    """Trả về (html_ket_qua, so_lan_da_thu) hoặc raise CaptchaError khi hết lượt thử."""
    driver.get(URL_TRA_CUU)
    _cho_trang_san_sang(driver)
    for lan_thu in range(1, max_retry_captcha + 1):
        _dien_form(driver, cccd)
        ma_captcha = solver.doc_captcha(driver, SELECTOR_CAPTCHA_IMG)
        logger.info(
            "CCCD=%s | thử CAPTCHA lần %d/%d | mã đọc được: %s",
            cccd, lan_thu, max_retry_captcha, ma_captcha,
        )
        _dien_captcha(driver, ma_captcha)
        _submit(driver)
        _cho_trang_san_sang(driver)  # chờ trang submit xong hẳn trước khi kiểm tra/điều hướng tiếp

        if _co_bang_ket_qua(driver):
            logger.info("CCCD=%s | CAPTCHA đúng ở lần thử %d/%d", cccd, lan_thu, max_retry_captcha)
            return driver.page_source, lan_thu

        logger.info(
            "CCCD=%s | lần thử %d/%d không có bảng kết quả (có thể do CAPTCHA sai hoặc không có dữ liệu)",
            cccd, lan_thu, max_retry_captcha,
        )
        if lan_thu < max_retry_captcha:
            _lam_moi_captcha(driver)

    # Hết lượt thử mà vẫn không có bảng kết quả: có thể do CAPTCHA sai liên tục
    # HOẶC dữ liệu thực sự không tồn tại (không thể phân biệt chắc chắn).
    raise CaptchaError(
        f"Không có bảng kết quả sau {max_retry_captcha} lần thử "
        "(có thể do CAPTCHA sai hoặc không tìm thấy dữ liệu)"
    )


def tra_cuu_voi_retry(
    driver: WebDriver,
    solver: CaptchaSolver,
    cccd: str,
    cfg: Config,
) -> LookupResult:
    for lan in range(1, cfg.max_retry_network + 1):
        try:
            html, so_lan_captcha = tra_cuu(driver, solver, cccd, cfg.max_retry_captcha)
            ket_qua = result_parser.parse(html, cccd)
            ket_qua.so_lan_thu_captcha = so_lan_captcha
            return ket_qua
        except CaptchaError as e:
            # Theo thiết kế: gán "Không tìm thấy" thay vì "Lỗi" vì không thể phân biệt
            # chắc chắn CAPTCHA sai với dữ liệu không tồn tại (xem docs mục 14, điểm 7).
            return LookupResult(
                cccd=cccd,
                trang_thai=TrangThai.KHONG_TIM_THAY,
                so_lan_thu_captcha=cfg.max_retry_captcha,
                ghi_chu=str(e),
            )
        except RateLimitError as e:
            if lan == cfg.max_retry_network:
                return LookupResult(cccd=cccd, trang_thai=TrangThai.LOI, ghi_chu=str(e))
            time.sleep(cfg.delay * 5)  # nghỉ lâu hơn nhiều so với delay thường để tránh bị chặn tiếp
        except (TimeoutException, WebDriverException) as e:
            if lan == cfg.max_retry_network:
                return LookupResult(cccd=cccd, trang_thai=TrangThai.LOI, ghi_chu=f"Lỗi kết nối: {e}")
            time.sleep(2)

    raise RuntimeError("Không thể xảy ra")  # an toàn cho type checker
