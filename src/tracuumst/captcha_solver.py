from __future__ import annotations

import os
import tempfile

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class CaptchaError(Exception):
    """Không nhận dạng đúng CAPTCHA sau số lần thử cho phép (BR-Rule-04)."""


class CaptchaSolver:
    """Tải ảnh CAPTCHA hiện tại trên trang và nhận dạng, tự động (OCR) hoặc thủ công nhanh (FR-04).

    engine:
    - "ddddocr" (mặc định): tự động nhận dạng bằng OCR, không cần con người.
    - "manual": mở ảnh CAPTCHA bằng trình xem ảnh mặc định và cho người dùng gõ nhanh qua console.
      Dùng khi độ chính xác OCR thấp trên thực tế, khiến chương trình phải thử lại CAPTCHA quá nhiều
      lần (chậm hơn so với để người dùng đọc và gõ trực tiếp).
    """

    def __init__(self, engine: str = "ddddocr"):
        self._engine = engine
        self._ocr = self._load_engine(engine)

    def _load_engine(self, engine: str):
        if engine == "ddddocr":
            import ddddocr

            return ddddocr.DdddOcr(show_ad=False)
        if engine == "manual":
            return None
        raise ValueError(f"OCR engine không hỗ trợ: {engine}")

    def doc_captcha(self, driver: WebDriver, captcha_img_selector: str) -> str:
        """Chụp ảnh CAPTCHA hiện tại trên trang và trả về chuỗi ký tự nhận dạng."""
        img_element: WebElement = driver.find_element("css selector", captcha_img_selector)
        image_bytes = img_element.screenshot_as_png
        if self._engine == "manual":
            return self._nhap_thu_cong(image_bytes)
        return self._ocr.classification(image_bytes).strip()

    def _nhap_thu_cong(self, image_bytes: bytes) -> str:
        """Mở ảnh CAPTCHA bằng trình xem ảnh mặc định của hệ điều hành và cho người dùng gõ nhanh."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(image_bytes)
            duong_dan = f.name
        try:
            os.startfile(duong_dan)  # type: ignore[attr-defined]  # chỉ có trên Windows
        except AttributeError:
            print(f"Không tự mở được ảnh, vui lòng mở thủ công: {duong_dan}")
        return input("Nhập mã CAPTCHA trong ảnh vừa mở rồi Enter: ").strip()

