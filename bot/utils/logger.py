import logging
from logging.handlers import RotatingFileHandler
import sys


def setup_logger():
    """
    Настраивает логгер:
    - Логирует в консоль (stdout)
    - Логирует в файл bot.log с ротацией (макс 5 файлов по 1MB)
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Обработчик для файла с ротацией
    file_handler = RotatingFileHandler(
        "bot.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
