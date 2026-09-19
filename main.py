import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from tracuumst import excel_io, gdt_client, validators
from tracuumst.captcha_solver import CaptchaSolver
from tracuumst.config import load
from tracuumst.logger import cau_hinh_logger
from tracuumst.models import LookupResult, TrangThai


def main() -> None:
    cfg = load()
    logger = cau_hinh_logger(cfg.log_file)

    ban_ghi = excel_io.doc_input(cfg.input, cfg.sheet, cfg.column)
    da_xong = excel_io.doc_ket_qua_da_co(cfg.output)
    logger.info("Đọc %d bản ghi từ %s, %d đã có kết quả 'Thành công' trước đó", len(ban_ghi), cfg.input, len(da_xong))
    logger.info(
        "Cấu hình: delay=%ss, max_retry_network=%s, max_retry_captcha=%s, timeout=%ss",
        cfg.delay, cfg.max_retry_network, cfg.max_retry_captcha, cfg.timeout,
    )

    solver = CaptchaSolver()
    driver = gdt_client.tao_driver(headless=cfg.headless)

    ket_qua_tong: list[LookupResult] = []
    try:
        for rec in ban_ghi:
            if rec.cccd in da_xong:
                ket_qua_tong.append(da_xong[rec.cccd])  # giữ lại nguyên vẹn kết quả cũ khi ghi đè output
                logger.info("CCCD=%s | bỏ qua (đã Thành công ở lần chạy trước)", rec.cccd)
                continue

            if not validators.kiem_tra_dinh_dang(rec.cccd):
                ket_qua_tong.append(LookupResult(cccd=rec.cccd, trang_thai=TrangThai.DINH_DANG_KHONG_HOP_LE))
                logger.info("CCCD=%s | trang_thai=%s", rec.cccd, TrangThai.DINH_DANG_KHONG_HOP_LE.value)
                continue

            ket_qua = gdt_client.tra_cuu_voi_retry(driver, solver, rec.cccd, cfg)
            ket_qua_tong.append(ket_qua)
            logger.info(
                "CCCD=%s | trang_thai=%s | so_lan_captcha=%s",
                ket_qua.cccd, ket_qua.trang_thai.value, ket_qua.so_lan_thu_captcha,
            )

            time.sleep(cfg.delay)  # FR-10: giới hạn tốc độ giữa các lượt tra cứu
    finally:
        driver.quit()
        excel_io.ghi_ket_qua(ket_qua_tong, cfg.output)

    so_thanh_cong = sum(1 for r in ket_qua_tong if r.trang_thai == TrangThai.THANH_CONG)
    logger.info(
        "Hoàn tất: %d bản ghi xử lý (bỏ qua %d đã xong trước đó), %d thành công. Kết quả tại %s",
        len(ket_qua_tong), len(da_xong), so_thanh_cong, cfg.output,
    )


if __name__ == "__main__":
    main()
