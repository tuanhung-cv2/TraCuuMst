import logging


def cau_hinh_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("tracuumst")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # tránh nhân đôi handler khi gọi lại nhiều lần (vd trong test)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(console_handler)

    return logger
