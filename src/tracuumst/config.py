import argparse
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    input: str
    sheet: str
    column: str
    output: str
    delay: float
    max_retry_network: int
    max_retry_captcha: int
    timeout: int
    headless: bool
    log_file: str


def _str_to_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


def load(argv: list[str] | None = None) -> Config:
    """Đọc cấu hình theo thứ tự ưu tiên: tham số CLI > biến môi trường (.env) > giá trị mặc định."""
    parser = argparse.ArgumentParser(description="Ứng dụng tra cứu MST theo CCCD/CMND")
    parser.add_argument("--input", default=os.getenv("INPUT_FILE", "input/danh_sach_cccd.xlsx"))
    parser.add_argument("--sheet", default=os.getenv("INPUT_SHEET", "DanhSachCCCD"))
    parser.add_argument("--column", default=os.getenv("CCCD_COLUMN", "CCCD"))
    parser.add_argument("--output", default=os.getenv("OUTPUT_FILE", "output/ket_qua_tra_cuu.xlsx"))
    parser.add_argument("--delay", type=float, default=float(os.getenv("REQUEST_DELAY_SECONDS", "4")))
    parser.add_argument("--max-retry-network", type=int, default=int(os.getenv("MAX_RETRY_NETWORK", "2")))
    parser.add_argument("--max-retry-captcha", type=int, default=int(os.getenv("MAX_RETRY_CAPTCHA", "3")))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15")))
    parser.add_argument(
        "--headless",
        type=_str_to_bool,
        default=_str_to_bool(os.getenv("HEADLESS_BROWSER", "true")),
    )
    parser.add_argument("--log-file", default=os.getenv("LOG_FILE", "tra_cuu.log"))

    args = parser.parse_args(argv)
    return Config(
        input=args.input,
        sheet=args.sheet,
        column=args.column,
        output=args.output,
        delay=args.delay,
        max_retry_network=args.max_retry_network,
        max_retry_captcha=args.max_retry_captcha,
        timeout=args.timeout,
        headless=args.headless,
        log_file=args.log_file,
    )
